#!/bin/bash

ERROR=1
SUCCESS=0

echo "Granting execution rights to the child bash scripts"
chmod -Rv +x $(find ./scripts -name "*.sh" -type f)
echo "Execution rights granted"

ENV_SETUP_SCRIPT="./scripts/ensure_env/ensure_env.sh"

if [ ! -x "$ENV_SETUP_SCRIPT" ]; then
    echo "Environement setup script $ENV_SETUP_SCRIPT is not present or not executable, aborting"
    exit $ERROR
fi

echo "Checking the environement integrity"
ENV_NAME="$($ENV_SETUP_SCRIPT)"
echo "Gathered environement name: $ENV_NAME"

echo "Activating environement..."
if [ -d "$ENV_NAME/bin" ] && [ -f "$ENV_NAME/bin/activate" ]; then
    chmod +x "$ENV_NAME/bin/activate"
    . "$ENV_NAME/bin/activate"
elif [ ! -d "$ENV_NAME/bin" ] && [ -d "$ENV_NAME/Scripts" ] && [ -f "$ENV_NAME/Scripts/activate" ]; then
    chmod +x "$ENV_NAME/Scripts/activate"
    . "$ENV_NAME/Scripts/activate"
else
    echo "No valid environment found on the current system, please make sure you are running on a real Linux/Mac system or WSL"
    exit $ERROR
fi

echo "Installing dependencies for the scripts to work..."
pip install -r ./requirements.scripts.txt
if [ $? -ne 0 ]; then
    echo "Failed to install dependencies, please check the requirements.scripts.txt file and your internet connection"
    exit $ERROR
fi

echo "Installing dependencies for the program..."
pip install -r ./requirements.txt
if [ $? -ne 0 ]; then
    echo "Failed to install dependencies, please check the requirements.txt file and your internet connection"
    exit $ERROR
fi
echo "Dependencies installed"

echo "Starting the router script..."
./scripts/router.sh
STATUS=$?
echo "The program exited with status code: $STATUS"
exit $STATUS
