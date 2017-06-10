@echo off

title Alert-nagios
set n=0
set sourceDir=%~dp0
REM echo %sourceDir%
reg query HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run | findstr /I /C:"Alert_ST.bat" >null || (
	echo add start... 
	reg add HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run /ve /t REG_SZ /d "%0"
)

where java >null
if errorlevel 0 (
	setlocal enabledelayedexpansion
		for /f "tokens=1,2* delims=." %%a in ('where java') do (
			set /a n+=1
			set ijava_!n!=%%~dpa
			REM set jjava_!n!=%%b
		)
		pushd "!ijava_1!" >null
			REM echo 123
			REM pause
			REM set tjava=!ijava_1!.!jjava_1!
			REM echo !ijava_1!
			REM echo 
			java -jar %sourceDir%\Alert_ST.jar 
			REM pause
		popd >null
	endlocal
	REM echo %tjava%
)

exit 0
REM pause
