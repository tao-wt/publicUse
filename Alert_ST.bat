@echo off

title add Alert-nagios autoStart
set n=0
set sourceDir=%~dp0
REM echo %sourceDir%

reg query HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run | findstr /I /C:"Alert_ST" >null || (
	echo add autoStart... 
	where javaw >null
	if errorlevel 0 (
		setlocal enabledelayedexpansion
			for /f "tokens=1,2* delims=." %%a in ('where javaw') do (
				set /a n+=1
				set ijava_!n!=%%~dpa
				REM set jjava_!n!=%%b
			)
			reg add HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run /v Alert_ST /t REG_SZ /d "!ijava_1! -jar %sourceDir%\Alert_ST.jar"
			REM pushd "!ijava_1!" >null
				REM pause
				REM set tjava=!ijava_1!.!jjava_1!
				REM echo !ijava_1!
				REM java -jar %sourceDir%\Alert_ST.jar 
				REM pause
			REM popd >null
		endlocal
		REM echo %tjava%
	) else goto javawError
)
echo *** add autoStart finishd! ***
exit 0
REM pause

:javawError
echo java maybe not install in your computer,please check.
exit 3
