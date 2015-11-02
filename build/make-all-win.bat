@echo off

if exist .\deploy\build del .\deploy\build\CONTROL\control
"%ProgramFiles(x86)%\Python26\python.exe" -O build.py
rem echo BUILD returned %ERRORLEVEL%!
If not %errorlevel% == 0 goto error

if exist .\deploy\build del .\deploy\build\CONTROL\control
"%ProgramFiles(x86)%\Python27\python.exe" -O build.py
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