@echo off
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :6004 ^| findstr LISTENING') do (
    echo Matando proceso con PID %%a
    taskkill /PID %%a /F
)
exit