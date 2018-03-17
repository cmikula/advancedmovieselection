@echo off

if exist .\deploy\build del .\deploy\build\CONTROL\control
"%ProgramFiles(x86)%\Python27\python.exe" -O build.py -t"deb" -a"all" -s"branches/oe22_unstable"
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