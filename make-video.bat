@echo off
setlocal

set "SCRIPT_DIR=%~dp0"

"%SCRIPT_DIR%ffmpeg.exe" -framerate 30 -i "%SCRIPT_DIR%timelapse_frames\%%06d.png" -c:v libx264 -pix_fmt yuv420p "%SCRIPT_DIR%timelapse.mp4"

endlocal
