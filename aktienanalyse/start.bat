@echo off
REM Startet die Aktienanalyse mit einem Doppelklick.
REM Beim ersten Start wird die virtuelle Umgebung angelegt und alles installiert.
cd /d "%~dp0"

if not exist .venv (
    echo Lege virtuelle Umgebung an ...
    python -m venv .venv || goto fehler
    echo Installiere Bibliotheken, das dauert beim ersten Mal ein paar Minuten ...
    .venv\Scripts\python -m pip install --upgrade pip
    .venv\Scripts\python -m pip install -r requirements.txt || goto fehler
)

.venv\Scripts\python -m streamlit run app.py
goto ende

:fehler
echo.
echo Es ist ein Fehler aufgetreten. Ist Python 3.11 oder neuer installiert?
pause

:ende
