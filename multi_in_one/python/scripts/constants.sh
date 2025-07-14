#!/bin/bash
#  +++++++++++++++++++++++++++++++++++++++++
#           Constants and variables
#  +++++++++++++++++++++++++++++++++++++++++

#  =========================================
#           The boolean constants
#  =========================================

# Boolean values
TRUE=0
FALSE=1

#  =========================================
#           The status constants
#  =========================================

SUCCESS=0
ERROR=1

#  =========================================
#           The debug mode togglers
#  =========================================

# Enter the debug mode once the main part of the program was run
DEBUG_MODE=$FALSE

# Enter debug mode when the main part of the program fails
DEBUG_ON_FAILURE=$FALSE

# The status of the debug mode
DEBUG_STATUS=$SUCCESS

# This is an internal variable to prevent the debug mode from being triggered multiple times
DEBUG_MODE_TRIGGERED=$FALSE
