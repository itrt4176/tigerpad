@echo off
TITLE TigerPad Relay

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
python -m pip install --upgrade pip

:updatedeps
call .venv\Scripts\activate.bat
pip install -r requirements.txt

:startrelay
py relay\relay.pyw