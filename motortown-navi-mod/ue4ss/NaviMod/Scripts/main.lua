-- NaviMod – zeigt die Minimap von Motor Town auf einem kaufbaren Navi-Teil an.
--
-- Ablauf:
--   1. Das Navi ist ein normales Anbauteil (wie die Lampen) aus NaviMod_P.pak.
--      Kaufen und Platzieren erledigt das Spiel selbst.
--   2. Dieses Skript sucht regelmaessig im Fahrzeug des Spielers nach Komponenten
--      mit dem Mesh "SM_Navi" und haengt an deren Display-Socket eine
--      WidgetComponent, die die Minimap des HUD rendert.

local UEHelpers = require("UEHelpers")
local config = require("config")

local MOD = "[NaviMod]"

local function Log(fmt, ...)
  print(string.format("%s " .. fmt .. "\n", MOD, ...))
end

local function Debug(fmt, ...)
  if config.Debug then Log(fmt, ...) end
end

-- Unreal-Enums (Werte aus den Engine-Headern)
local EWidgetSpace_World = 0
local EWidgetBlendMode_Opaque = 0
local EAttachmentRule_KeepRelative = 0
local EAttachmentRule_SnapToTarget = 2

local classCache = {}
local function Class(path)
  local cls = classCache[path]
  if cls == nil or not cls:IsValid() then
    cls = StaticFindObject(path)
    classCache[path] = cls
  end
  return cls
end

local function VehicleClass() return Class("/Script/MotorTown.MTVehicle") end
local function HudClass() return Class("/Script/MotorTown.MotorTownInGameHUD") end
local function StaticMeshComponentClass() return Class("/Script/Engine.StaticMeshComponent") end
local function WidgetComponentClass() return Class("/Script/UMG.WidgetComponent") end
local function WidgetLibrary() return Class("/Script/UMG.Default__WidgetBlueprintLibrary") end
local function CanvasPanelClass() return Class("/Script/UMG.CanvasPanel") end
local function CanvasPanelSlotClass() return Class("/Script/UMG.CanvasPanelSlot") end

-- Zustand
local screens = {}        -- [Adresse der Navi-Komponente] = { navi, widgetComp }
local enabled = true
local moved = nil         -- "move"-Modus: { widget, parent, layout, zOrder, owner }

---------------------------------------------------------------------------
-- HUD / Minimap
---------------------------------------------------------------------------

local function GetPlayerController()
  local pc = UEHelpers.GetPlayerController()
  if pc and pc:IsValid() then return pc end
  return nil
end

local function GetHudMinimap(pc)
  local hud = pc:GetHUD()
  if not hud:IsValid() or not hud:IsA(HudClass()) then return nil end
  local hudWidget = hud.HUDWidget
  if not hudWidget or not hudWidget:IsValid() then return nil end
  local minimap = hudWidget.MinimapWidget
  if not minimap or not minimap:IsValid() then return nil end
  return minimap
end

-- "move"-Modus: HUD-Minimap aus dem HUD loesen, Position merken
local function TakeHudMinimap(minimap, owner)
  if moved then return nil end
  local slot = minimap.Slot
  local entry = { widget = minimap, owner = owner }
  if slot and slot:IsValid() then
    entry.parent = slot.Parent
    if slot:IsA(CanvasPanelSlotClass()) then
      entry.layout = slot:GetLayout()
      entry.zOrder = slot:GetZOrder()
    end
  end
  minimap:RemoveFromParent()
  moved = entry
  Debug("HUD-Minimap ins Navi verschoben")
  return minimap
end

-- "move"-Modus: HUD-Minimap an ihren alten Platz zuruecklegen
local function RestoreHudMinimap()
  if not moved then return end
  local m = moved
  moved = nil
  if not m.widget:IsValid() then return end
  if m.owner and m.owner:IsValid() then
    pcall(function() m.owner:SetWidget(nil) end)
  end
  if m.parent and m.parent:IsValid() then
    local slot
    if m.parent:IsA(CanvasPanelClass()) then
      slot = m.parent:AddChildToCanvas(m.widget)
    else
      slot = m.parent:AddChild(m.widget)
    end
    if slot and slot:IsValid() and m.layout then
      slot:SetLayout(m.layout)
      slot:SetZOrder(m.zOrder or 0)
    end
  end
  Debug("HUD-Minimap zurueck im HUD")
end

local function CreateMinimapWidget(pc, widgetComp)
  local minimap = GetHudMinimap(pc)
  if not minimap then return nil end

  if config.Mode == "move" then
    return TakeHudMinimap(minimap, widgetComp)
  end

  local widget = WidgetLibrary():Create(UEHelpers.GetWorld(), minimap:GetClass(), pc)
  if widget and widget:IsValid() then return widget end
  Log("Konnte Minimap-Widget %s nicht erzeugen", minimap:GetClass():GetFullName())
  return nil
end

---------------------------------------------------------------------------
-- Display am Navi
---------------------------------------------------------------------------

local function DestroyScreen(key)
  local s = screens[key]
  screens[key] = nil
  if not s then return end
  if moved and moved.owner == s.widgetComp then
    RestoreHudMinimap()
  end
  if s.widgetComp:IsValid() then
    s.widgetComp:K2_DestroyComponent(s.widgetComp)
  end
end

local function AttachScreen(pc, vehicle, navi)
  local widgetComp = vehicle:AddComponentByClass(
    WidgetComponentClass(), true,
    { Rotation = { X = 0, Y = 0, Z = 0, W = 1 }, Translation = { X = 0, Y = 0, Z = 0 }, Scale3D = { X = 1, Y = 1, Z = 1 } },
    false)
  if not widgetComp or not widgetComp:IsValid() then
    Log("WidgetComponent konnte nicht erzeugt werden")
    return nil
  end

  local socket = FName(config.ScreenSocket or "None")
  local hasSocket = config.ScreenSocket ~= nil and navi:DoesSocketExist(socket)
  widgetComp:K2_AttachToComponent(navi, hasSocket and socket or FName("None"),
    EAttachmentRule_SnapToTarget, EAttachmentRule_SnapToTarget, EAttachmentRule_KeepRelative, false)
  if not hasSocket then
    widgetComp:K2_SetRelativeLocation(config.ScreenOffset, false, {}, true)
  end
  widgetComp:K2_SetRelativeRotation(config.ScreenRotation, false, {}, true)

  -- Pixel -> cm: Widget mit DrawSize.X Pixeln soll ScreenWidthCm breit sein
  local scale = config.ScreenWidthCm / config.DrawSize.X
  widgetComp:SetRelativeScale3D({ X = scale, Y = scale, Z = scale })

  widgetComp:SetWidgetSpace(EWidgetSpace_World)
  widgetComp:SetDrawSize(config.DrawSize)
  widgetComp:SetPivot({ X = 0.5, Y = 0.5 })
  widgetComp:SetTwoSided(true)
  widgetComp:SetBlendMode(EWidgetBlendMode_Opaque)
  widgetComp:SetBackgroundColor({ R = 0, G = 0, B = 0, A = 1 })
  widgetComp:SetTickWhenOffscreen(false)
  widgetComp:SetRedrawTime(config.RedrawInterval)
  widgetComp:SetCollisionEnabled(0)

  widgetComp:SetVisibility(enabled, true)

  Log("Navi-Display an %s angebracht (Socket: %s)", vehicle:GetFName():ToString(), hasSocket and config.ScreenSocket or "keiner")
  return widgetComp
end

local function IsNavi(comp)
  local mesh = comp.StaticMesh
  return mesh and mesh:IsValid() and mesh:GetFName():ToString() == config.NaviMeshName
end

---------------------------------------------------------------------------
-- Suche
---------------------------------------------------------------------------

local function Scan()
  -- Aufraeumen: Navi entfernt oder Fahrzeug weg
  for key, s in pairs(screens) do
    if not s.navi:IsValid() or not s.widgetComp:IsValid() or not IsNavi(s.navi) then
      DestroyScreen(key)
    end
  end

  local pc = GetPlayerController()
  if not pc then return end
  local pawn = pc:K2_GetPawn()

  if not pawn:IsValid() or not pawn:IsA(VehicleClass()) then
    -- Zu Fuss: im "move"-Modus gehoert die Minimap wieder ins HUD
    if moved then RestoreHudMinimap() end
    return
  end

  local comps = pawn:K2_GetComponentsByClass(StaticMeshComponentClass())
  for i = 1, #comps do
    local comp = comps[i]
    if comp:IsValid() and IsNavi(comp) then
      local key = comp:GetAddress()
      local s = screens[key]
      if not s then
        local widgetComp = AttachScreen(pc, pawn, comp)
        if widgetComp then
          s = { navi = comp, widgetComp = widgetComp, hasWidget = false }
          screens[key] = s
        end
      end
      -- Minimap einsetzen: beim ersten Mal, falls das HUD noch nicht bereit war,
      -- und im "move"-Modus nach Aus- und Wiedereinsteigen
      if s and (not s.hasWidget or (config.Mode == "move" and not moved)) then
        local widget = CreateMinimapWidget(pc, s.widgetComp)
        if widget then
          s.widgetComp:SetWidget(widget)
          s.hasWidget = true
        end
      end
    end
  end
end

LoopAsync(config.ScanIntervalMs, function()
  ExecuteInGameThread(function()
    local ok, err = pcall(Scan)
    if not ok then Log("Fehler: %s", tostring(err)) end
  end)
  return false -- weiterlaufen
end)

---------------------------------------------------------------------------
-- Taste: Displays an/aus
---------------------------------------------------------------------------

local key = Key[config.ToggleKey]
if key then
  RegisterKeyBind(key, function()
    ExecuteInGameThread(function()
      enabled = not enabled
      for _, s in pairs(screens) do
        if s.widgetComp:IsValid() then s.widgetComp:SetVisibility(enabled, true) end
      end
      Log("Navi-Displays %s", enabled and "an" or "aus")
    end)
  end)
end

Log("geladen (Modus: %s, Mesh: %s)", config.Mode, config.NaviMeshName)
