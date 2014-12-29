@echo off

if exist .\deploy\build del .\deploy\build\CONTROL\control
"%ProgramFiles%\Python27\python.exe" -O build.py -sbranches/OE2.2 -tdeb
If not %errorlevel% == 0 goto error

goto success

:error
echo *** BUILD ERROR ***
pause

:success
echo *************************
echo ***   BUILD SUCCESS   ***
echo *************************
rem pause