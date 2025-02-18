#!/bin/bash

# !!! Execute from the root of the repository

# install mkdocs
pip install mkdocs
pip install mkdocs-material
pip install mkdocs-autorefs
pip install mkdocstrings[python]

# Start mkdocs serve in the background
mkdocs serve &
MKDOCS_PID=$!

# Wait for mkdocs serve to start
sleep 10

# Ask user to continue
read -p "Documentation is running locally at http://127.0.0.1:8000. Continue build and deploy? (Y/n): " answer

# Stop mkdocs serve
kill $MKDOCS_PID

# Check user input
if [[ "$answer" =~ ^([Yy]|[Yy][Ee][Ss])$ ]] || [[ -z "$answer" ]]; then
    echo "Building and deploying documentation..."
    mkdocs build && mkdocs gh-deploy
else
    echo "Exiting..."
fi
