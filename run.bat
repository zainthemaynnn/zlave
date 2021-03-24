@echo off
if not defined VIRTUAL_ENV (call .\env\Scripts\activate)
echo zlave is ONLINE
py -3 src/zlave.py
echo zlave is OFFLINE
echo/
cmd /k