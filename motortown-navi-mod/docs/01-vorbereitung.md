# 1. Vorbereitung

Diese Schritte machst du einmal auf deinem Windows-PC, auf dem Motor Town installiert ist.

## Werkzeuge

| Werkzeug | Wofür | Download |
|---|---|---|
| **UE4SS** (experimental) | Lua-Mods ausführen, `.usmap` erzeugen | https://github.com/UE4SS-RE/RE-UE4SS/releases (Tag `experimental-latest`) |
| **AES Dumpster** | Schlüssel der Spieldateien auslesen | https://github.com/GHFear/AESDumpster |
| **FModel** | Spieldateien ansehen, Tabellen finden | https://fmodel.app |
| **UAssetGUI** | Tabelle bearbeiten (Zeile klonen) | https://github.com/atenfyr/UAssetGUI/releases |
| **repak** | Pak packen | https://github.com/trumank/repak/releases |
| **Unreal Engine 5.5** | Modell kochen (über Epic Games Launcher) | gleiche Hauptversion wie das Spiel, siehe unten |
| **Blender 4.x** | Navi-Modell erzeugen | https://www.blender.org |

## Engine-Version prüfen

`MotorTown\Binaries\Win64\MotorTown-Win64-Shipping.exe` → Rechtsklick → Eigenschaften → Details →
**Produktversion**. Laut Community-Guide war das zuletzt `5.5.4.0`, also **UE 5.5**.
Installiere genau diese Haupt- und Nebenversion (5.5). Mit einer anderen Version gekochte Dateien lädt das Spiel nicht.

## AES-Schlüssel

Ziehe `MotorTown-Win64-Shipping.exe` auf `AESDumpster.exe` und kopiere den Schlüssel (`0x…`).

## Mapping-Datei (.usmap)

Ohne `.usmap` kann FModel bzw. UAssetGUI die Tabellen nicht lesen.

1. Kopiere UE4SS (`dwmapi.dll` + Ordner `ue4ss`) nach `MotorTown\Binaries\Win64\`.
2. Setze in `ue4ss\UE4SS-settings.ini`:
   ```ini
   [Debug]
   GuiConsoleEnabled = 1
   GuiConsoleVisible = 1
   ```
3. Starte das Spiel. Im UE4SS-Fenster: **Dumpers → Generate .usmap file**.
4. Die Datei liegt danach in `Binaries\Win64\` (bzw. `ue4ss\`). Kopiere sie z. B. nach `Dokumente\MotorTownModding\Mappings.usmap`.

> Lass UE4SS danach **installiert**, die Lua-Mod braucht es.
> (`GuiConsoleVisible` kannst du später wieder auf 0 stellen.)

## FModel einrichten

1. **Settings**: Game Directory = `…\MotorTown\Content\Paks`, UE-Version = `GAME_UE5_5`.
2. Bei **Mapping File** die `.usmap` von oben eintragen.
3. **Directory → AES**: Schlüssel eintragen. Danach siehst du links den Inhalt von `MotorTown-Windows.pak`.

Weiter mit [2. Navi-Modell](02-navi-modell.md).
