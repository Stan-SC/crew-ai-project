#!/bin/bash

# Activation de l'environnement virtuel
source .venv/bin/activate

# Installation des packages nécessaires
pip install flask crewai python-dotenv

# Création du dossier templates s'il n'existe pas
mkdir -p templates

echo "Installation terminée. Pour lancer le serveur, exécutez:"
echo "source .venv/bin/activate && python crew_server.py" 