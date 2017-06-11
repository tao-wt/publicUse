@echo off

title add Alert-nagios autoStart
set n=0
set sourceDir=%~dp0
REM echo %sourceDir%

reg query HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run | findstr /I /C:"Alert_ST" >null || (
	echo add autoStart... 
	REM where javaw >null 2>&1
	REM if errorlevel 0 (
	where javaw >null 2>&1 && (
		setlocal enabledelayedexpansion
			for /f "tokens=1,2* delims=." %%a in ('where javaw') do (
				set /a n+=1
				set ijava_!n!=%%~dpa
				REM set jjava_!n!=%%b
			)
			reg add HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run /v Alert_ST /t REG_SZ /d "!ijava_1! -jar %sourceDir%\Alert_ST.jar" || goto regError
			REM pushd "!ijava_1!" >null
				REM pause
				REM set tjava=!ijava_1!.!jjava_1!
				REM echo !ijava_1!
				REM java -jar %sourceDir%\Alert_ST.jar 
				REM pause
			REM popd >null
		endlocal
		goto addOk
		REM echo %tjava%
	)
	REM ) else goto javawError
	where javaw >null 2>&1 || goto javawError
)
echo *** Alert_ST autostart had added! ***
ping 127.0.0.1 -n 5 >null
exit 0


:addOk
echo *** add autoStart finishd! cmd window close after 5s. ***
ping 127.0.0.1 -n 5 >null
exit 0

:javawError
echo *** java maybe not install in your computer,please check. ***
REM pause
exit 2


:regError
echo *** reg add failed,please check! ***
REM pause
exit 1