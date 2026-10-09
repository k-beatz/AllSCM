@echo off
rem Baut NaviMod_P.pak aus den gekochten Unreal-Dateien und der geaenderten Teile-Tabelle.
rem
rem Aufruf:  pack.bat "C:\Pfad\zum\UE-Projekt\MotorTown"
rem
rem Erwartet:
rem   - repak.exe im PATH (https://github.com/trumank/repak/releases)
rem   - gekochtes Projekt:  <Projekt>\Saved\Cooked\Windows\MotorTown\Content\Mods\NaviMod\
rem   - geaenderte Tabelle:  ..\build\table\  (gleiche Ordnerstruktur ab MotorTown\Content\...)
setlocal

set "PROJECT=%~1"
set "ROOT=%~dp0.."
set "STAGE=%ROOT%\build\NaviMod_P"
set "COOKED=%PROJECT%\Saved\Cooked\Windows\MotorTown\Content\Mods\NaviMod"

if "%PROJECT%"=="" (
  echo Bitte den Pfad zum Unreal-Projekt angeben, z.B. pack.bat "D:\UE\MotorTown"
  exit /b 1
)
if not exist "%COOKED%" (
  echo Gekochte Dateien nicht gefunden: %COOKED%
  echo Im Unreal Editor zuerst Platforms ^> Windows ^> Cook Content ausfuehren.
  exit /b 1
)
where repak >nul 2>nul || (
  echo repak.exe nicht gefunden. Download: https://github.com/trumank/repak/releases
  exit /b 1
)

if exist "%STAGE%" rmdir /s /q "%STAGE%"
mkdir "%STAGE%\MotorTown\Content\Mods\NaviMod"
xcopy /e /y /q "%COOKED%\*" "%STAGE%\MotorTown\Content\Mods\NaviMod\" >nul

if exist "%ROOT%\build\table\MotorTown" (
  xcopy /e /y /q "%ROOT%\build\table\MotorTown\*" "%STAGE%\MotorTown\" >nul
) else (
  echo WARNUNG: build\table fehlt - das Navi ist dann nicht im Shop kaufbar.
)

del /s /q "%STAGE%\*.bak" >nul 2>nul

repak pack --version V11 "%STAGE%" "%ROOT%\build\NaviMod_P.pak" || exit /b 1
echo.
echo Fertig: %ROOT%\build\NaviMod_P.pak
echo Kopieren nach: ...\MotorTown\Content\Paks\
