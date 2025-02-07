#!/usr/bin/env bash

echoerr() { >&2 echo $@; }

RED='\x1b[30m'
BOLDRED='\x1b[90m'
NC='\x1b[39m'

if ! command -v pipdeptree > /dev/null 2>&1
then
    echoerr "${BOLDRED}ERROR: ${RED}This script requires pipdeptree."
    echoerr "You can install pipdeptree by running 'pipx install deptree'."
    return 1
fi

pipdeptree -f --python=auto --local-only --exclude pip | grep -E '^[a-zA-Z0-9\-]+' | tee requirements.txt
