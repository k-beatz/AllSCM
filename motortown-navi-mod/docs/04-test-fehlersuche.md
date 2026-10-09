# 4. Testen und Fehlersuche

## Installation prüfen

```
MotorTown\
├── Binaries\Win64\
│   ├── dwmapi.dll
│   └── ue4ss\Mods\NaviMod\
│       ├── enabled.txt
│       └── Scripts\main.lua, config.lua
└── Content\Paks\
    ├── MotorTown-Windows.pak
    └── NaviMod_P.pak
```

## Test

1. Spiel starten. In der UE4SS-Konsole bzw. in `ue4ss\UE4SS.log` muss stehen:
   `[NaviMod] geladen (Modus: instance, Mesh: SM_Navi)`
2. Zum Car Supply Store fahren. Das **Navi** steht in der Liste der Anbauteile.
3. Kaufen und am Armaturenbrett anbringen. Fürs Erste ist das Display schwarz.
4. Einsteigen. Nach höchstens einer Sekunde sollte im Log `[NaviMod] Navi-Display an … angebracht` stehen,
   und im Rahmen läuft die Minimap.
5. Mit **F7** schaltest du das Display aus und wieder ein.

## Typische Fehler

| Problem | Ursache / Lösung |
|---|---|
| Kein `[NaviMod] geladen` im Log | `enabled.txt` fehlt, oder der Ordner liegt nicht unter `ue4ss\Mods\`. Alternativ in `ue4ss\Mods\mods.txt` die Zeile `NaviMod : 1` eintragen. |
| Navi nicht im Shop | Das Pak wird nicht geladen (Name endet nicht auf `_P`), die Tabelle liegt im falschen Ordner, oder es ist die falsche Tabelle. Mit FModel das eigene Pak öffnen und Pfade vergleichen. |
| Spiel stürzt beim Start ab | Die Tabelle passt nicht zur Spielversion (nach einem Update neu exportieren) oder ist beim Bearbeiten kaputtgegangen. Pak entfernen, Schritt 3 wiederholen. |
| Navi unsichtbar, Platz trotzdem belegt | Das Mesh wird nicht gefunden: Mesh-Pfad in der Tabelle prüfen, `SM_Navi` mit UE **5.5** und **ohne Io Store** kochen. |
| Navi sichtbar, Display bleibt schwarz | Im Log steht kein „angebracht“: `NaviMeshName` in `config.lua` muss genau dem Mesh-Namen entsprechen. Für die Fehlersuche `Debug = true` setzen. |
| Display leer, Log sagt „angebracht“ | Die Kopie der Minimap wird nicht aktualisiert. In `config.lua` **`Mode = "move"`** setzen: Dann wandert die echte HUD-Minimap ins Navi und kommt beim Aussteigen zurück. |
| Bild spiegelverkehrt oder auf dem Kopf | `ScreenRotation` in `config.lua`: `Yaw = 180` bzw. `Roll = 180`. |
| Minimap zu groß oder zu klein im Rahmen | `ScreenWidthCm` muss zur Displaybreite passen (12 cm). Seitenverhältnis über `DrawSize` anpassen. |
| Ruckler | `RedrawInterval` erhöhen, z. B. `1/15`, oder `DrawSize` verkleinern. |
| `Fehler: …` im Log | Komplette Zeile kopieren und melden. Meist hat sich mit einem Spiel-Update ein Klassen- oder Feldname geändert. |

## Nützliche UE4SS-Werkzeuge

* **Live View** (UE4SS-Fenster): Suche nach `SM_Navi` zeigt, ob und an welchem Fahrzeug das Teil hängt.
* Suche nach `MinimapWidget` zeigt die Klasse der Minimap. Gut zu wissen, falls sich der Name bei einem Update ändert.
