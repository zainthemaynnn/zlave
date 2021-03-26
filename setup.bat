@echo off
echo initializing...
if not exist env\ (python -m venv env)
if not defined VIRTUAL_ENV (call env\Scripts\activate)

py -3 -m pip install -U discord.py
py -3 -m pip install -U PyYAML
py -3 -m pip install -U youtube_dl

if not exist data\App_Data.db (sqlite3.exe data\App_Data.db < templates\schema.sql)
if not exist data\keywords.json (type templates\keywords.json >> data\keywords.json)

echo/ & echo welcome to the extremely janky and halfhearted zlave setup wizard
echo a virtual environment and some packages have already been installed
echo you will need to install ffmpeg and sqlite to path yourself if you want to use voice or the database features
pause & echo/

py -3 tools\initialize.py

echo congrats, your bot is now configured. check /data/zlave.log to see what he's doing.
echo you may now skip setup.bat and use run.bat
pause & echo/

call run.bat
