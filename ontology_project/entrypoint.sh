#!/bin/bash

if [ "$1" = 'api' ]; then
    # Run the FastAPI API
    uvicorn main:app --host 0.0.0.0 --port 8000
elif [ "$1" = 'cli' ]; then
    shift
    python main.py "$@"
else
    echo "Usage: api | cli [args]"
    exit 1
fi
