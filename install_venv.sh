#! /bin/bash

VENV_NAME=.venv-rando
python3 -m venv ${VENV_NAME}

. ./${VENV_NAME}/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

# Hint how to activate
echo source ./${VENV_NAME}/bin/activate



