ECHO OFF
FOR /F "tokens=*" %%A IN ('DATE/T') DO FOR %%B IN (%%A) DO SET Today=%%B

FOR /F "tokens=1-3 delims=/-" %%A IN ("%Today%") DO (
    SET Dia=%%A
    SET Mes=%%B
    SET Anio=%%C
)

SET FILENAMELOG=%Anio%-%Mes%-%Dia%
echo %FILENAMELOG%
ECHO OFF
cd C:\Users\ValkUser\Documents\quadmind
SET PY_EXE=python.exe
%PY_EXE% C:\Users\ValkUser\Documents\quadmind\main.py >> c:\LOGS\quadmind-%FILENAMELOG%.txt 2>&1 