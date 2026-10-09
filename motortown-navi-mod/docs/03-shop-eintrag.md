# 3. Navi in den Shop bringen

Lampen und andere Anbauteile kommen im Spiel aus einer Daten-Tabelle (DataTable oder DataAsset).
Darin hat jedes Teil eine Zeile mit Name, Preis, Mesh und weiteren Werten. Für das Navi **klonst du die Zeile
eines vorhandenen Anbauteils** und änderst nur Name, Preis und Mesh. Das Platzieren am Fahrzeug funktioniert dann von
selbst, weil das Spiel das Navi wie jedes andere Anbauteil behandelt.

> Wie die Tabelle heißt und welche Felder sie hat, ist nicht öffentlich dokumentiert. Du findest es
> einmalig mit FModel heraus (3.1). Die Felder unten in *Kursiv* sind Vermutungen, typisch für Motor Town.
> Halte dich an das, was du in FModel siehst.

## 3.1 Tabelle finden (FModel)

1. Links unter `MotorTown/Content/DataAsset/` suchen. Dort liegen auch `Cargos` und
   `GameResource` aus dem Economy-Guide.
2. **Package → Search** (Strg+Shift+F) nach Begriffen wie `Attachment`, `Accessor`, `Light`, `Part`, `Vehicle`.
3. Öffne die Kandidaten per Doppelklick und prüfe, ob du die Lampen aus dem Car Supply Store wiederfindest,
   z. B. einen Arbeitsscheinwerfer, eine Lichtleiste oder einen LED-Streifen. Achte auf:
   * Zeilennamen (Row Names) wie *`Light_…`* oder *`Attachment_…`*
   * ein Feld mit einem Mesh-Pfad (`/Game/…/SM_….SM_…`)
   * Preis-Feld (*`Cost`*, *`Price`*), Anzeigename (*`Name`*, *`DisplayName`*, `FText`)
   * eventuell Kategorie bzw. Shop-Zuordnung (*`Category`*, *`ShopType`*, *`Vendor`*)
4. Notiere den **Pfad der Tabelle** (z. B. `MotorTown/Content/DataAsset/<Name>.uasset`) und den
   **Zeilennamen einer geeigneten Vorlage**:
   * **Am besten** ein Anbauteil **ohne** Licht, falls es so etwas gibt (Deko, Antenne o. Ä.).
   * Gibt es nur Lampen, nimm die kleinste Lampe. In 3.3 stellst du dann das Licht ab.

## 3.2 Tabelle exportieren

In FModel Rechtsklick auf die Tabelle → **Export Raw Data (.uasset)**. Du bekommst `.uasset` und `.uexp`.
Lege beide mit der **gleichen Ordnerstruktur** hier ab:

```
motortown-navi-mod/build/table/MotorTown/Content/DataAsset/<Name>.uasset
motortown-navi-mod/build/table/MotorTown/Content/DataAsset/<Name>.uexp
```

(Steckt die Tabelle in einem anderen Ordner, übernimmst du diesen Ordner.)

## 3.3 Zeile klonen (UAssetGUI)

1. Öffne UAssetGUI. **Utils → Import Mappings** → `.usmap` laden, rechts oben auswählen, Engine-Version **5.5** einstellen.
2. Öffne `build/table/…/<Name>.uasset`.
3. Gehe zu **Export Data → Table Info** bzw. zu den Zeilen und suche die Vorlage-Zeile.
4. Rechtsklick auf die Zeile → **Duplicate**. Dann in der Kopie ändern:

   | Feld | Neuer Wert |
   |---|---|
   | Row Name | `NaviMod_Navi` |
   | Anzeigename | `Navi` |
   | Preis | z. B. `450` |
   | Mesh | `/Game/Mods/NaviMod/SM_Navi.SM_Navi` |
   | Licht (falls Lampe als Vorlage) | Helligkeit/Intensität `0`, Licht-Modus *aus/None* |

5. **Mesh-Pfad:** In UE5 sind Soft-Referenzen meist zwei Namen, Paket und Asset:
   `/Game/Mods/NaviMod/SM_Navi` und `SM_Navi`.
   Neue Namen musst du in UAssetGUI zuerst in der **Name Map** anlegen (Rechtsklick → Add). Erst danach kannst du sie in der Zeile eintragen.
   Ist das Mesh-Feld stattdessen ein *Import* (Objekt-Referenz statt Text), lege unter **Import Data**
   zwei Imports an: `Package /Game/Mods/NaviMod/SM_Navi` und `StaticMesh SM_Navi` (Outer = das Package).
   Kopiere am besten die Imports der Original-Lampe und ändere nur die Namen.
6. Speichern. Die `.bak`-Dateien löscht `pack.bat` automatisch.

## 3.4 Pak bauen

```bat
tools\pack.bat "D:\UE\MotorTown"
```

Kopiere `build\NaviMod_P.pak` nach `…\MotorTown\Content\Paks\`. Das `_P` am Ende ist wichtig: Daran erkennt das Spiel,
dass es diese Dateien bevorzugt laden soll.

## Plan B, falls das Mesh-Feld nicht klappt

Lass das Mesh der Vorlage-Zeile unverändert und ändere nur Name und Preis. Setze dann in `config.lua`
`NaviMeshName` auf den **Mesh-Namen der Vorlage**, z. B. `SM_WorkLight_01`.
Die Lua-Mod hängt die Minimap dann an dieses Teil. Es sieht nicht wie ein Navi aus, aber so kannst du testen,
ob Shop, Platzieren und Minimap funktionieren. Danach kümmerst du dich um das eigene Modell.

> Achtung: Bei Plan B bekommen **alle** Teile mit diesem Mesh ein Display, also auch die echten Lampen dieses Typs.

Weiter mit [4. Test & Fehlersuche](04-test-fehlersuche.md).
