#!/bin/bash

if [ "$1" = 'api' ]; then
    # Lancer le serveur FastAPI depuis le dossier `app`
    uvicorn app.main:app --host 0.0.0.0 --port 8000
elif [ "$1" = 'cli' ]; then
    shift
    # Exécuter le script en mode CLI
    python -m app.main "$@"
else
    echo "Usage: api | cli [args]"
    exit 1
fi
