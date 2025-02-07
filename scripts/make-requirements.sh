#!/usr/bin/env bash

echoerr() { >&2 echo $@; }

RED='\x1b[0;31m'
BOLDRED='\x1b[1;31m'
NC='\x1b[0;39m'

if ! command -v pipdeptree > /dev/null 2>&1
then
    echoerr -e "${BOLDRED}ERROR: ${RED}This script requires pipdeptree.${NC}"
    echoerr -e "Run 'pip install -r requirements-dev.txt' to resolve this error."
    exit 1
fi

echo "pygobject==3.50.0; sys_platform=='linux'" > requirements.txt
pipdeptree -f --python=auto --local-only --exclude pip,pipdeptree,pygobject,pycairo | grep -E '^[a-zA-Z0-9\-]+' | tee -a requirements.txt
