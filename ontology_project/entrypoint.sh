#!/bin/bash

if [ "$1" = 'api' ]; then
    # Run the FastAPI API
    uvicorn app:app --host 0.0.0.0 --port 8000
elif [ "$1" = 'cli' ]; then
    # Run the script in CLI
    shift
    python main.py "$@"
else
    echo "Usage: api | cli [args]"
    exit 1
fi
