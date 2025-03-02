# CrewAI Project

Application de gestion d'équipe IA utilisant CrewAI avec une interface de visualisation moderne.

## Structure du Projet

- `crew_server.py` : Serveur Flask backend avec l'API REST
- `crew-dashboard/` : Application React frontend
- `templates/` : Templates HTML pour l'interface utilisateur

## Configuration Requise

### Backend
- Python 3.9
- Flask
- CrewAI
- python-dotenv

### Frontend
- Node.js 16.x
- React 18
- Material-UI
- Nivo pour les visualisations

## Installation

1. Backend :
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Frontend :
```bash
cd crew-dashboard
npm install
```

## Démarrage

1. Backend :
```bash
python crew_server.py
```

2. Frontend :
```bash
cd crew-dashboard
npm start
```

## Fonctionnalités

- Dashboard interactif pour la visualisation de l'équipe
- Gestion des agents IA avec CrewAI
- Interface moderne et responsive
- Graphiques en temps réel
- Gestion des tâches et du statut 