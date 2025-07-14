#!/bin/bash

SUCCESS=0
FAILURE=1

TRUE=0
FALSE=1

CWD="$(pwd)"

SCRIPTS_DIR="$CWD/scripts"

CONTINUE_LOOPING=$TRUE

PYTHON_FOUND=$FALSE
PYTHON=NULL
command -v python3 --version 2>/dev/null 1>&2
PY3=$?
command -v python --version 2>/dev/null 1>&2
PY=$?
command -v py --version 2>/dev/null 1>&2
PYP=$?
if [ $PY3 -eq 0 ]; then
    PYTHON=python3
    PYTHON_FOUND=$TRUE
elif [ $PY -eq 0 ]; then
    PYTHON=python
    PYTHON_FOUND=$TRUE
elif [ $PYP -eq 0 ]; then
    PYTHON=py
    PYTHON_FOUND=$TRUE
else
    echo "Router: No python version found on your computer (or it's PATH variable), disabling options relying on python"
    PYTHON_FOUND=$FALSE
fi
# As none of the python overlay functionalities are implemented yet, it is disabled
PYTHON_FOUND=$FALSE

function compile {
    echo "compile"
    ${SCRIPTS_DIR}/compile/compile.sh
    return $?
}

function coverage {
    echo "coverage"
    ${SCRIPTS_DIR}/coverage/coverage.sh
    return $?
}

function document {
    echo "document"
    ${SCRIPTS_DIR}/document/document.sh
    return $?
}

function library {
    echo "library"
    ${SCRIPTS_DIR}/lib/lib.sh
    return $?
}

function tester {
    echo "tester"
    ${SCRIPTS_DIR}/test/test.sh
    return $?
}

function run_raw {
    echo "run_raw"
    ${SCRIPTS_DIR}/run_raw/run_raw.sh
    return $?
}

function version {
    echo "version"
    ${SCRIPTS_DIR}/version/version.sh
    return $?
}

function help_section {
    echo "help"
    ${SCRIPTS_DIR}/helper/helper.sh
    return $?
}

function author {
    echo "Author"
    echo "These sets of scripts were written by (c) Henry Letellier"
    echo "They are provided as if and without any warranty"
    return $SUCCESS
}

function about {
    echo "about"
    ${SCRIPTS_DIR}/about/about.sh
    return $?
}

function gui {
    echo "gui"
    $PYTHON ${SCRIPTS_DIR}/gui
    return $?
}

function tui {
    echo "tui"
    $PYTHON ${SCRIPTS_DIR}/tui
    return $?
}

echo "Debug:"
echo "* CWD: $CWD"
echo "* Scripts: $SCRIPTS_DIR"

echo "Welcome to the router script!"
author
echo ""
while [ $CONTINUE_LOOPING -eq $TRUE ]; do
    echo "Router menu options:"
    echo -n "(com)pile (cov)erage (d)ocument (l)ibrary (te)ster (r)un_raw (v)ersion (h)elp (au)thor (ab)out "
    if [ $PYTHON_FOUND -eq $TRUE ]; then
        echo -n "(g)ui (tu)i "
    fi
    echo "(q)uit (e)xit"
    read -p "Please enter the option you wish to use: " USER_RESPONSE
    USER_RESPONSE=$(echo $USER_RESPONSE | tr "ABCDEFGHIJKLMNOPQRSTUVWXYZ" "abcdefghijklmnopqrstuvwxyz")
    case $USER_RESPONSE in
    com*)
        compile
        ;;
    cov*)
        coverage
        ;;
    d*)
        document
        ;;
    l*)
        library
        ;;
    te*)
        tester
        ;;
    r*)
        run_raw
        ;;
    v*)
        version
        ;;
    h*)
        help_section
        ;;
    au*)
        author
        ;;
    ab*)
        about
        ;;
    g*)
        if [ $PYTHON_FOUND -eq $TRUE ]; then
            gui
        else
            echo "Python is not present on your system, thus this command is disabled"
        fi
        ;;
    tu*)
        if [ $PYTHON_FOUND -eq $TRUE ]; then
            tui
        else
            echo "Python is not present on your system, thus this command is disabled"
        fi
        ;;
    q* | e*)
        echo "Exiting the router menu..."
        CONTINUE_LOOPING=$FALSE
        ;;
    *)
        echo "Option '$USER_RESPONSE' not found in provided options"
        ;;
    esac
done
