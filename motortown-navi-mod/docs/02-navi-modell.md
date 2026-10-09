# 2. Navi-Modell erzeugen und kochen

## 2.1 FBX mit Blender erzeugen

```bat
blender --background --python blender\make_navi_mesh.py -- build\SM_Navi.fbx
```

Alternativ öffnest du das Skript in Blender unter **Scripting → Run Script**. Ergebnis ist `SM_Navi.fbx`:

| Teil | Material | Maße |
|---|---|---|
| Halterung (hinten, Ursprung) | `M_NaviMount` | 3 × 3 × 1,5 cm |
| Gehäuse | `M_NaviFrame` | 14 × 11 × 2 cm |
| Rahmen um das Display | `M_NaviFrame` | 1 cm breit, 0,4 cm hoch |
| Displayfläche | `M_NaviScreen` | 12 × 9 cm |

Achsen wie in Unreal: **+X zeigt aus dem Display heraus**, der Ursprung liegt hinten an der Halterung.
Größe oder Form kannst du oben im Skript ändern. Änderst du die Displaygröße, musst du
`ScreenWidthCm` und `DrawSize` in `config.lua` anpassen.

## 2.2 Unreal-Projekt anlegen

1. Lege in UE 5.5 ein neues Projekt an: **Games → Blank**, Blueprint, ohne Starter Content.
2. Nenne das Projekt **genau `MotorTown`**. Nur dann landen die gekochten Dateien unter dem Pfad
   `MotorTown/Content/…`, den das Spiel als `/Game/…` lädt.
3. Lege im Content Browser den Ordner **`Content/Mods/NaviMod`** an.

## 2.3 Importieren

1. Ziehe `SM_Navi.fbx` in `Mods/NaviMod`.
2. Einstellungen im Import-Dialog: *Combine Meshes* an, *Generate Missing Collision* aus,
   *Material Import Method* = Create New Materials.
3. Öffne `SM_Navi` und prüfe, ob das Display in **+X** zeigt. Dafür im Viewport oben links
   **Show → Pivot** einschalten. Zeigt es woandershin: Mesh schließen, neu importieren und im Dialog
   *Import Rotation* so setzen, dass das Display nach +X schaut.
4. Materialien (optional schöner machen):
   * `M_NaviFrame`: Base Color fast schwarz, Roughness 0,4
   * `M_NaviScreen`: Base Color schwarz, Roughness 0,1. Das sieht man nur bei ausgeschaltetem Display.

## 2.4 Socket für das Display

Im Static Mesh Editor: **Window → Socket Manager → Create Socket**

| Feld | Wert |
|---|---|
| Name | `Screen` |
| Relative Location | X = **3.6**, Y = 0, Z = 0 |
| Relative Rotation | 0, 0, 0 |

Der Socket liegt genau zwischen Displayfläche (X = 3,55) und Rahmenkante (X = 3,9). Dort zeichnet die
Lua-Mod die Minimap hin. Der Socket ist optional: Fehlt er, nimmt die Mod `ScreenOffset` aus `config.lua`, und das ergibt dieselbe Position.

## 2.5 Kochen

1. **Edit → Project Settings → Packaging**: *Use Io Store* **aus** und *Use Pak File* an.
   Unter *Additional Asset Directories to Cook* den Ordner `/Game/Mods/NaviMod` eintragen.
2. **Platforms → Windows → Cook Content**.
3. Die Dateien liegen danach in
   `MotorTown\Saved\Cooked\Windows\MotorTown\Content\Mods\NaviMod\`
   (`SM_Navi.uasset/.uexp/.ubulk`, `M_Navi*.uasset/.uexp`).

`tools\pack.bat` holt die Dateien dort automatisch ab.

Weiter mit [3. Shop-Eintrag](03-shop-eintrag.md).
