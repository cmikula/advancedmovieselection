@echo off

if exist .\deploy\build del .\deploy\build\CONTROL\control
rem "%ProgramFiles(x86)%\Python26\python.exe" -O build.py -tipk
rem echo BUILD returned %ERRORLEVEL%!
If not %errorlevel% == 0 goto error

if exist .\deploy\build del .\deploy\build\CONTROL\control
"%ProgramFiles(x86)%\Python27\python.exe" -O build.py -t"ipk" -a"all"
If not %errorlevel% == 0 goto error

rem build oe22
if exist .\deploy\build del .\deploy\build\CONTROL\control
"%ProgramFiles(x86)%\Python27\python.exe" -O build.py -t"deb" -a"all" -s"branches/oe22_unstable"
If not %errorlevel% == 0 goto error

rem build oe25
if exist .\deploy\build del .\deploy\build\CONTROL\control
"%ProgramFiles(x86)%\Python27\python.exe" -O build.py -t"deb" -a"all" -s"branches/oe25_unstable" -d"enigma2 (>= 4.3.1r24)"
If not %errorlevel% == 0 goto error


if exist .\deploy\build del .\deploy\build\CONTROL\control
rem "%ProgramFiles(x86)%\Python27\python.exe" -O build.py -sbranches/all_oe -tdeb
"%ProgramFiles(x86)%\Python27\python.exe" -O build.py -t"deb" -a"all"
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