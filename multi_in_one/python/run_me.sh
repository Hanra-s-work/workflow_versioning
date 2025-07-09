#!/bin/bash
echo "Attributing rights to the scripts located in the scripts directory."
chmod +x -R scripts/*.sh
echo "starting router.sh"
./scripts/router.sh
STATUS=$?
if [ $STATUS -ne 0 ]; then
    echo "An error occurred while running the router or one of it's children."
    exit $STATUS
else
    echo "The router ran successfully executed successfully."
fi
