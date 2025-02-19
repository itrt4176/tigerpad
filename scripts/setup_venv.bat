@echo off
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

cls