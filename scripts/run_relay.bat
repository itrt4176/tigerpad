@echo off
TITLE TigerPad Relay

IF EXIST relay.pid (
    GOTO stoprelay
) ELSE (
    GOTO checkvenv
)

:stoprelay
FOR /F "tokens=*" %%p IN (relay.pid) DO taskkill /pid %%p

:checkvenv
CALL scripts\setup_venv.bat

:startrelay
pyw.exe relay\relay.pyw