@echo off
TITLE TigerPad Relay
SETCONSOLE /hide

IF EXIST relay.pid (
    GOTO stoprelay
) else (
    GOTO runupdate
)

:stoprelay
FOR /F "tokens=*" %%p IN (relay.pid) DO taskkill /pid %%p

:runupdate
git pull

IF EXIST .venv\ (
    GOTO updatedeps
) else (
    GOTO createvenv
)

:createvenv
py -m venv .venv

:updatedeps
call .venv\Scripts\activate.bat
pip install -r requirements.txt

:startrelay
py host_relay_client\relay.py