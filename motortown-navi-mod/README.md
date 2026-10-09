# NaviMod für Motor Town: Behind The Wheel

Ein Navi zum Kaufen und frei Platzieren, so wie die Lampen. Im Rahmen des Navis läuft die
**normale Minimap des Spiels** live mit.

```
 ┌──────────────────────┐
 │ ┌──────────────────┐ │  ← Rahmen (Mesh SM_Navi)
 │ │                  │ │
 │ │  Minimap (live)  │ │  ← WidgetComponent, erzeugt von UE4SS-Lua
 │ │                  │ │
 │ └──────────────────┘ │
 └──────────┬───────────┘
            ▀  ← Halterung = Befestigungspunkt am Fahrzeug
```

## So funktioniert's

Die Mod besteht aus zwei Teilen, die zusammenarbeiten:

| Teil | Datei | Aufgabe |
|---|---|---|
| **Pak-Mod** | `NaviMod_P.pak` | Bringt das 3D-Modell `SM_Navi` (Gehäuse, Rahmen, Display, Halterung) ins Spiel und trägt das Navi als **Anbauteil im Shop** ein. Kaufen, Platzieren, Verschieben und Drehen übernimmt das Spiel selbst, genau wie bei den Lampen. |
| **Lua-Mod** | `ue4ss/NaviMod/` | Läuft mit [UE4SS](https://github.com/UE4SS-RE/RE-UE4SS). Sucht jede Sekunde im Fahrzeug, in dem du sitzt, nach Teilen mit dem Mesh `SM_Navi`. Auf deren Display hängt sie eine `WidgetComponent`, die die Minimap aus dem HUD (`HUD.HUDWidget.MinimapWidget`) anzeigt. |

Warum zwei Teile? Ein Pak kann Modelle und Tabellen liefern, aber keine neue Logik.
Mit Lua lässt sich die Minimap umleiten, ein Shop-Artikel lässt sich damit aber nicht sauber anlegen.

## Stand

| Was | Status |
|---|---|
| Lua-Skript (Display-Logik, Taste F7, Einstellungen) | ✅ fertig, Syntax geprüft. **Im Spiel noch nicht getestet.** |
| Blender-Skript für das Navi-Modell | ✅ fertig und getestet (erzeugt `SM_Navi.fbx`, 14 × 11 × 3,9 cm) |
| Pack-Skript `tools/pack.bat` | ✅ fertig |
| Modell in Unreal 5.5 importieren und kochen | 🔧 Schritt auf deinem PC, siehe [docs/02-navi-modell.md](docs/02-navi-modell.md) |
| Shop-Eintrag (Zeile in der Anbauteile-Tabelle) | 🔧 Schritt auf deinem PC, siehe [docs/03-shop-eintrag.md](docs/03-shop-eintrag.md) |

Die Tabelle mit den Anbauteilen steckt verschlüsselt in den Spieldateien und ist nicht öffentlich dokumentiert.
Deshalb musst du sie einmal selbst mit FModel suchen. Die Anleitung sagt dir genau, wonach du suchst.

## Ordner

```
motortown-navi-mod/
├── README.md                     ← diese Datei
├── docs/
│   ├── 01-vorbereitung.md        ← Werkzeuge, AES-Key, Spieldateien entpacken
│   ├── 02-navi-modell.md         ← Blender → Unreal → gekochte Dateien
│   ├── 03-shop-eintrag.md        ← Navi in den Shop bringen (Tabelle klonen)
│   └── 04-test-fehlersuche.md    ← Testen, typische Fehler
├── blender/make_navi_mesh.py     ← erzeugt SM_Navi.fbx
├── tools/pack.bat                ← baut NaviMod_P.pak
└── ue4ss/NaviMod/                ← Lua-Mod (kommt nach ue4ss/Mods/)
    ├── enabled.txt
    └── Scripts/
        ├── main.lua
        └── config.lua            ← alle Einstellungen
```

## Reihenfolge

1. [Vorbereitung](docs/01-vorbereitung.md): Werkzeuge installieren, Spieldateien lesbar machen
2. [Navi-Modell](docs/02-navi-modell.md): Modell erzeugen, in Unreal importieren, kochen
3. [Shop-Eintrag](docs/03-shop-eintrag.md): eine Anbauteil-Zeile klonen und auf das Navi umbiegen
4. `tools\pack.bat "<UE-Projekt>"` ausführen, dann `build\NaviMod_P.pak` nach `MotorTown\Content\Paks\` kopieren
5. UE4SS installieren und `ue4ss/NaviMod` nach `MotorTown\Binaries\Win64\ue4ss\Mods\NaviMod` kopieren
6. [Testen](docs/04-test-fehlersuche.md)

## Bedienung im Spiel

* Navi im **Car Supply Store** (dort, wo es die Lampen gibt) kaufen und wie eine Lampe am Fahrzeug anbringen,
  am besten aufs Armaturenbrett oder an die Scheibe.
* Einsteigen: Nach etwa einer Sekunde erscheint die Minimap im Navi.
* **F7** blendet alle Navi-Displays ein und aus.
* Einstellungen in `Scripts/config.lua`: Taste, Auflösung, Bildrate, Modus.

## Wichtig

* **Mehrspieler:** Jeder Spieler braucht Pak und Lua-Mod. Ohne die Mod sehen andere Spieler
  ein unsichtbares Teil. Die Minimap zeigt immer **deine** Karte. Auch wenn du in einem fremden Fahrzeug sitzt, siehst du deine Position.
* **Deinstallieren:** Baue das Navi im Spiel zuerst ab. Sonst bleibt es unsichtbar am Fahrzeug und belegt einen
  der 10 Anbauplätze.
* **Spiel-Updates:** Die Lua-Mod sollte Updates meist überstehen. Die geklonte Tabelle im Pak ersetzt
  aber die Original-Tabelle. Nach einem Update deshalb Schritt 3 mit der neuen Tabelle wiederholen,
  sonst fehlen neue Teile aus dem Update oder das Spiel stürzt ab.
* Andere Mods, die dieselbe Tabelle ändern, vertragen sich nicht mit dieser Mod. Es gewinnt immer das Pak, das zuletzt geladen wird.

## Quellen

* UE4SS: https://github.com/UE4SS-RE/RE-UE4SS · Lua-Doku: https://docs.ue4ss.com
* Klassennamen (`MTVehicle`, `MotorTownInGameHUD`, `HUDWidget.MinimapWidget`) stammen aus der
  Server-Mod [drpsyko101/MotorTownMods](https://github.com/drpsyko101/MotorTownMods)
* Pak-Workflow (AES, usmap, UAssetGUI, `_P`-Pak): [motor-town-economy-mod-guide](https://github.com/jamescodesthings/motor-town-economy-mod-guide)
