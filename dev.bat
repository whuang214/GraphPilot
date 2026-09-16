@echo off
REM Double-click this to start GraphPilot. It opens the app in your browser and keeps
REM this window as the log; closing the window or pressing Ctrl+C stops both servers.
REM
REM The window is deliberately kept open on failure: double-clicked scripts that close
REM instantly take the error message with them.

setlocal
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" run.py %*
) else (
  python run.py %*
)

if errorlevel 1 (
  echo.
  echo GraphPilot exited with an error. The message is above.
  pause
)
endlocal
