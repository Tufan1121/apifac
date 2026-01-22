@echo off
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3700 ^| findstr LISTENING') do (
    echo Matando proceso con PID %%a
    taskkill /PID %%a /F
)
exit