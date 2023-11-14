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
%PY_EXE% C:\Users\ValkUser\Documents\quadmind\main_planned_routes.py >> c:\LOGS\quadmind-planned-routes-%FILENAMELOG%.txt 2>&1 



set RUN=C:\Users\ValkUser\Downloads\pdi-ce-8.0.0.0-28\data-integration
set FILE_RUN=C:\Users\ValkUser\Downloads\pdi-ce-8.0.0.0-28\data-integration\src\Deposito\quadmind
%RUN%\Kitchen.bat /file "%FILE_RUN%\main_status.kjb"  >> c:\LOGS\quadmind-planned-routes-%FILENAMELOG%.txt 2>&1 