-- NaviMod – Einstellungen
-- Alle Werte koennen hier angepasst werden, ohne main.lua anzufassen.

return {
  -- Name des Static Mesh aus dem Pak (ohne Pfad). Jede Fahrzeug-Komponente,
  -- die dieses Mesh benutzt, bekommt ein Display mit der Minimap.
  NaviMeshName = "SM_Navi",

  -- Socket im Mesh, auf dem das Display sitzt. Die X-Achse des Sockets zeigt
  -- aus dem Display heraus (zum Fahrer). Fehlt der Socket, wird der
  -- Mesh-Ursprung plus ScreenOffset benutzt.
  ScreenSocket = "Screen",
  ScreenOffset = { X = 3.6, Y = 0.0, Z = 0.0 },      -- cm, nur ohne Socket (passt zu SM_Navi)
  ScreenRotation = { Pitch = 0.0, Yaw = 0.0, Roll = 0.0 }, -- Yaw = 180, falls das Bild spiegelverkehrt ist

  -- Sichtbare Displaygroesse in cm (Mesh-Einheiten, vor Skalierung durch den Spieler).
  -- Muss zur Displayflaeche im Mesh passen (Blender-Skript: 12 x 9 cm).
  ScreenWidthCm = 12.0,

  -- Aufloesung, mit der die Minimap gerendert wird (Seitenverhaeltnis = Display).
  DrawSize = { X = 480, Y = 360 },

  -- Wie oft das Display neu gezeichnet wird (Sekunden). 0 = jeden Frame.
  RedrawInterval = 1.0 / 30.0,

  -- "instance": eigene Kopie der Minimap im Navi, HUD-Minimap bleibt.
  -- "move":     die HUD-Minimap wandert ins Navi (verschwindet vom Bildschirm).
  --             Fallback, falls "instance" leer/schwarz bleibt.
  Mode = "instance",

  -- Wie oft (ms) nach Navis im aktuellen Fahrzeug gesucht wird.
  ScanIntervalMs = 1000,

  -- Taste zum Ein-/Ausblenden aller Navi-Displays.
  ToggleKey = "F7",

  -- Ausfuehrliche Logs in UE4SS.log / Konsole.
  Debug = false,
}
