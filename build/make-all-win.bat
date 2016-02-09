@echo off

if exist .\deploy\build del .\deploy\build\CONTROL\control
"%ProgramFiles(x86)%\Python26\python.exe" -O build.py -tipk
rem echo BUILD returned %ERRORLEVEL%!
If not %errorlevel% == 0 goto error

if exist .\deploy\build del .\deploy\build\CONTROL\control
"%ProgramFiles(x86)%\Python27\python.exe" -O build.py -tipk
If not %errorlevel% == 0 goto error

if exist .\deploy\build del .\deploy\build\CONTROL\control
rem "%ProgramFiles(x86)%\Python27\python.exe" -O build.py -sbranches/all_oe -tdeb
"%ProgramFiles(x86)%\Python27\python.exe" -O build.py -tdeb
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