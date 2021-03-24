@echo off
if not exist env\ (python -m venv env)
if not defined VIRTUAL_ENV (call env\Scripts\activate)

py -3 -m pip install -U discord.py
py -3 -m pip install -U PyYAML
py -3 -m pip install -U youtube_dl

set "PYTHONPATH=%cd%"
if not exist data\App_Data.db (sqlite3.exe data\App_Data.db < data\schema.sql)

echo/ & echo welcome to the extremely janky and halfhearted zlave setup wizard
echo a virtual environment and some packages have already been installed
echo you will need to install ffmpeg and sqlite to path yourself if you want to use voice or the database features
pause

echo/ & echo every discord bot has a "client token". to get one:
echo -go to discord.com/developers
echo -click "create a bot"
echo -click "copy" under "token"
echo keep it safe, others can use it to hack your bot
set /p zlave_token="CLIENT TOKEN: "

echo/ & echo every user has a "user id". to get one:
echo -go to the discord app
echo -enable "developer mode" in settings
echo -right click yourself and click "copy id"
echo the bot uses this to recognize you as its operator
set /p zlave_owner="OWNER ID: "

echo/ & echo congrats, your bot is now configured. check /data/zlave.log to see what he's doing.
echo you may now skip setup.bat and skip to run.bat
echo however note that upon closing this window, you will have to run setup.bat again
echo if you wish to run this across multiple sessions, I recommend you paste your client id and user id somewhere safe
echo/
pause

call run.bat