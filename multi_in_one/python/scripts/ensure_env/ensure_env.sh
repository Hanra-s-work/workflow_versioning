#!/bin/bash

ERROR=1
SUCCESS=0
TRUE=0
FALSE=1

MAC_SYSTEM="$(uname | tr "ABDEFGHIJKLMNOPQRSTUVWXYZ" "abdefghijklmnopqrstuvwxyz")"
MY_SYSTEM="$(uname --kernel-name | tr "ABDEFGHIJKLMNOPQRSTUVWXYZ" "abdefghijklmnopqrstuvwxyz")"

function ech_info {
    echo "$@" >&2
}

function determine_env_name {
    if [ "$MY_SYSTEM" == "linux" ] || [ "$MAC_SYSTEM" == "linux" ]; then
        MY_ENV='lenv'
    elif [ "$MAC_SYSTEM" == "darwin" ]; then
        MY_ENV='menv'
    else
        ech_info "OS probably not supported"
        ech_info "This program has nor been tested on your system"
        MY_ENV="env_unix"
    fi
    echo "$MY_ENV"
}

function get_python_binary {
    E="$(python3 --version >/dev/null 2>&1)"
    STATUS_PYTHON3=$?
    E="$(python --version >/dev/null 2>&1)"
    STATUS_PYTHON=$?
    E="$(py --version >/dev/null 2>&1)"
    STATUS_PY=$?
    if [ $STATUS_PYTHON3 -ne 0 ] && [ $STATUS_PYTHON -ne 0 ] && [ $STATUS_PY -ne 0 ]; then
        ech_info "You do not have python installed, please install Python 3.x and relaunch this script"
        ech_info "Aborting program"
        exit $ERROR
    elif [ $STATUS_PYTHON3 -eq 0 ]; then
        echo "python3"
        return
    elif [ $STATUS_PYTHON -eq 0 ]; then
        echo "python"
        return
    elif [ $STATUS_PY -eq 0 ]; then
        echo "py"
        return
    fi
}

function get_pip_binary {
    pip3 --version >/dev/null 2>&1
    STATUS_PIP3=$?
    pip --version >/dev/null 2>&1
    STATUS_PIP=$?
    python3 -m pip --version >/dev/null 2>&1
    STATUS_PYTHON3_PIP=$?
    if [ $STATUS_PIP -ne 0 ] && [ $STATUS_PIP3 -ne 0 ] && [ $STATUS_PYTHON_PIP -ne 0 ]; then
        ech_info "You do not have pip installed, please install pip and relaunch this script"
        ech_info "Aborting program"
    elif [ $STATUS_PIP -eq 0 ]; then
        echo "pip"
        return
    elif [ $STATUS_PIP3 -eq 0 ]; then
        echo "pip3"
        return
    fi
}

if [ $# -eq 0 ]; then
    CWD="$(pwd)"
else
    CWD="$1"
fi
if [ $# -ge 2 ]; then
    ENV_NAME="$2"
else
    ENV_NAME="$(determine_env_name)"
fi
PYTHON="$(get_python_binary)"
PIP="$(get_pip_binary)"

ech_info "Debug : "
ech_info "* MY_SYSTEM: $MY_SYSTEM"
ech_info "* MAC_SYSTEM: $MAC_SYSTEM"
ech_info "* nb args: $#"
ech_info "* CWD: $CWD"
ech_info "* ENV_NAME: $ENV_NAME"
ech_info "* PYTHON: $PYTHON"
ech_info "* PIP: $PIP"

ech_info "Entering: $CWD"
cd "$CWD"

FRESH_ENV=$FALSE

ech_info "Checking if the environment already exists..."
if [ ! -d "$ENV_NAME" ]; then
    ech_info "Creating environment $ENV_NAME..."
    $PYTHON -m venv "$ENV_NAME" 1>&2
    FRESH_ENV=$TRUE
else
    ech_info "Environment $ENV_NAME already exists, skipping creation"
fi

ech_info "Testing environement activation..."
ech_info "Checking if patching is required (due to semi unix like environment)..."
if [ -d "$CWD/$ENV_NAME/bin" ] && [ -f "$CWD/$ENV_NAME/bin/activate" ]; then
    ech_info "Environement does not need patching"
    chmod +x "$CWD/$ENV_NAME/bin/activate"
    . "$CWD/$ENV_NAME/bin/activate" 1>&2
elif [ ! -d "$CWD/$ENV_NAME/bin" ] && [ -d "$CWD/$ENV_NAME/Scripts" ] && [ -f "$CWD/$ENV_NAME/Scripts/activate" ]; then
    ech_info "Environement patched for semi unix like environment"
    chmod +x "$CWD/$ENV_NAME/Scripts/activate"
    . "$CWD/$ENV_NAME/Scripts/activate" 1>&2
else
    ech_info "No valid environement found on the current system, please make sure you are running on a real Linux/Mac system"
    exit $ERROR
fi
ech_info "Patching checked"

if [ $FRESH_ENV -eq $TRUE ]; then
    ech_info "Updating pip..."
    $PYTHON -m pip install --upgrade pip 1>&2
fi
ech_info "Desactivating environement..."
deactivate 1>&2

ech_info "Exporting the environement path..."
echo "$CWD/$ENV_NAME"
exit $SUCCESS
