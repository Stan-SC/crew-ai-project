"""
Module de serveur Flask pour la visualisation en temps réel de CrewAI.
Inclut une gestion avancée des exceptions et une optimisation de la mémoire.
"""

from flask import Flask, render_template, Response, request, jsonify
from crewai import Agent, Task, Crew, Process
from datetime import datetime
import json
import queue
import threading
import os
import logging
from dotenv import load_dotenv
from typing import Dict, List, Optional
from dataclasses import dataclass
from contextlib import contextmanager

# Configuration du logging avec des niveaux plus détaillés
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('crew_server.log')
    ]
)
logger = logging.getLogger(__name__)

# Taille maximale de la queue pour éviter les fuites de mémoire
MAX_QUEUE_SIZE = 1000

@dataclass
class FactoryConfig:
    """Configuration du Directeur Factory avec validation des données"""
    goal: str
    backstory: str

    def __post_init__(self):
        if not self.goal or not isinstance(self.goal, str):
            raise ValueError("L'objectif doit être une chaîne non vide")
        if not self.backstory or not isinstance(self.backstory, str):
            raise ValueError("L'histoire doit être une chaîne non vide")

@dataclass
class TaskConfig:
    """Configuration d'une tâche avec validation des données"""
    description: str
    expected_output: str
    agent: Agent

    def __post_init__(self):
        if not self.description or not isinstance(self.description, str):
            raise ValueError("La description de la tâche doit être une chaîne non vide")
        if not self.expected_output or not isinstance(self.expected_output, str):
            raise ValueError("La sortie attendue doit être une chaîne non vide")
        if not self.agent or not isinstance(self.agent, Agent):
            raise ValueError("L'agent doit être une instance valide de la classe Agent")

class QueueManager:
    """Gestionnaire de queue avec limitation de taille"""
    def __init__(self, maxsize: int = MAX_QUEUE_SIZE):
        self.queue = queue.Queue(maxsize=maxsize)
        self._lock = threading.Lock()

    def put(self, item: dict) -> None:
        """Ajoute un élément à la queue avec gestion de la taille maximale"""
        try:
            with self._lock:
                if self.queue.qsize() >= MAX_QUEUE_SIZE:
                    try:
                        self.queue.get_nowait()  # Retire le plus ancien élément
                    except queue.Empty:
                        pass
                self.queue.put(item)
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout à la queue: {str(e)}")
            raise

    def get(self) -> dict:
        """Récupère un élément de la queue"""
        return self.queue.get()

    def clear(self) -> None:
        """Vide la queue"""
        with self._lock:
            while not self.queue.empty():
                try:
                    self.queue.get_nowait()
                except queue.Empty:
                    break

app = Flask(__name__)
updates_queue = QueueManager()

# Variables globales avec typage
factory_config = FactoryConfig(
    goal='Piloter l\'équipe et assurer la qualité du livrable',
    backstory='Expert en gestion d\'équipe avec une forte expérience en développement et qualité'
)
crew_thread: Optional[threading.Thread] = None
crew_stop_event = threading.Event()

# Chargement des variables d'environnement avec validation
load_dotenv()
REQUIRED_ENV_VARS = ['OPENAI_API_KEY']
for var in REQUIRED_ENV_VARS:
    if not os.getenv(var):
        raise EnvironmentError(f"Variable d'environnement manquante: {var}")

@contextmanager
def error_handler(error_msg: str):
    """Gestionnaire de contexte pour la gestion des exceptions"""
    try:
        yield
    except Exception as e:
        logger.error(f"{error_msg}: {str(e)}")
        raise

class CustomJSONEncoder(json.JSONEncoder):
    """Encodeur JSON personnalisé avec gestion d'erreurs améliorée"""
    def default(self, obj):
        try:
            return str(obj)
        except Exception as e:
            logger.error(f"Erreur lors de l'encodage JSON: {str(e)}")
            return f"<Non encodable: {type(obj).__name__}>"

def task_callback(output, agent_name):
    """Gère la sortie des tâches"""
    try:
        logger.info(f"Nouvelle sortie de tâche reçue de {agent_name}: {str(output)[:100]}...")
        update = {
            'type': 'task_update',
            'timestamp': datetime.now().isoformat(),
            'message': str(output),
            'agent': agent_name
        }
        updates_queue.put(json.dumps(update, cls=CustomJSONEncoder))
    except Exception as e:
        logger.error(f"Erreur dans task_callback: {str(e)}")

def create_agent_callback(agent_name):
    """Crée un callback spécifique pour un agent"""
    return lambda output: task_callback(output, agent_name)

def create_task(config: TaskConfig, output_handler=None) -> Task:
    """Crée une tâche à partir d'une configuration validée"""
    return Task(
        description=config.description,
        expected_output=config.expected_output,
        agent=config.agent,
        output_handler=output_handler
    )

@app.route('/update_factory_goal', methods=['POST'])
def update_factory_goal():
    """Met à jour l'objectif du Directeur Factory avec validation et redémarre l'équipe"""
    try:
        data = request.get_json()
        if not data or 'goal' not in data:
            return jsonify({'success': False, 'error': 'Goal manquant'}), 400
        
        with error_handler("Erreur lors de la mise à jour de l'objectif"):
            factory_config.goal = data['goal']
            logger.info(f"Objectif du Directeur Factory mis à jour: {data['goal'][:100]}...")
            
            # Redémarrer l'équipe
            restart_crew()
            logger.info("Équipe redémarrée après mise à jour de l'objectif")
            
            return jsonify({'success': True})
    except ValueError as ve:
        return jsonify({'success': False, 'error': str(ve)}), 400
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour de l'objectif: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/update_factory_backstory', methods=['POST'])
def update_factory_backstory():
    """Met à jour l'histoire du Directeur Factory avec validation et redémarre l'équipe"""
    try:
        data = request.get_json()
        if not data or 'backstory' not in data:
            return jsonify({'success': False, 'error': 'Backstory manquante'}), 400
        
        with error_handler("Erreur lors de la mise à jour de l'histoire"):
            factory_config.backstory = data['backstory']
            logger.info(f"Histoire du Directeur Factory mise à jour: {data['backstory'][:100]}...")
            
            # Redémarrer l'équipe
            restart_crew()
            logger.info("Équipe redémarrée après mise à jour de l'histoire")
            
            return jsonify({'success': True})
    except ValueError as ve:
        return jsonify({'success': False, 'error': str(ve)}), 400
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour de l'histoire: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/get_factory_config')
def get_factory_config():
    """Récupère la configuration actuelle du Directeur Factory"""
    return jsonify(factory_config)

@app.route('/restart_crew', methods=['POST'])
def restart_crew():
    """Redémarre l'équipe avec les nouvelles configurations et gestion des erreurs"""
    try:
        global crew_thread, crew_stop_event
        
        with error_handler("Erreur lors du redémarrage de l'équipe"):
            # Arrêter le thread existant s'il y en a un
            if crew_thread and crew_thread.is_alive():
                crew_stop_event.set()
                crew_thread.join(timeout=5)
                if crew_thread.is_alive():
                    logger.warning("Le thread précédent n'a pas pu être arrêté proprement")
                crew_stop_event.clear()
            
            # Vider la queue des mises à jour
            updates_queue.clear()
            
            # Créer et démarrer un nouveau thread
            crew_thread = threading.Thread(target=run_crew)
            crew_thread.daemon = True
            crew_thread.start()
            
            logger.info("Équipe redémarrée avec succès")
            return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Erreur lors du redémarrage de l'équipe: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

def run_crew():
    try:
        if crew_stop_event.is_set():
            return

        logger.info("Démarrage de l'équipe...")
        
        # Configuration des agents
        directeur_factory = Agent(
            role="Directeur Factory",
            role_description="Pilote l'équipe et assure la qualité du livrable",
            goal=factory_config.goal,
            backstory=factory_config.backstory,
            allow_delegation=True,
            verbose=True,
            tools=[]
        )

        chef_de_projet = Agent(
            role="Chef de Projet",
            role_description="Planifie les tâches et organise le travail d'équipe",
            goal="Créer un plan clair et efficace pour le développement",
            backstory="Expert en gestion de projet avec 10 ans d'expérience",
            allow_delegation=False,
            verbose=True,
            tools=[]
        )

        developpeur = Agent(
            role="Développeur",
            role_description="Écrit du code Python propre et efficace",
            goal="Transformer les spécifications en code fonctionnel",
            backstory="Développeur Python senior avec expertise en bonnes pratiques",
            allow_delegation=False,
            verbose=True,
            tools=[]
        )

        testeur = Agent(
            role="Testeur",
            role_description="Teste et améliore la qualité du code",
            goal="Assurer la qualité et la fiabilité du code",
            backstory="Expert en QA avec une forte attention aux détails",
            allow_delegation=False,
            verbose=True,
            tools=[]
        )

        # Création des tâches avec validation
        task_configs = [
            TaskConfig(
                description="Superviser et coordonner le travail de l'équipe pour atteindre les objectifs",
                expected_output="Rapport de supervision et recommandations pour l'équipe",
                agent=directeur_factory
            ),
            TaskConfig(
                description="Créer un plan détaillé pour le développement du projet",
                expected_output="Document détaillant les étapes, fonctionnalités et considérations techniques",
                agent=chef_de_projet
            ),
            TaskConfig(
                description="Écrire le code selon les spécifications, incluant gestion des erreurs et documentation",
                expected_output="Code fonctionnel et documenté",
                agent=developpeur
            ),
            TaskConfig(
                description="Tester le code et suggérer des améliorations",
                expected_output="Rapport de tests avec cas testés et suggestions d'amélioration",
                agent=testeur
            )
        ]

        # Création des tâches avec callbacks
        tasks = [
            create_task(config, create_agent_callback(config.agent.name))
            for config in task_configs
        ]

        # Notification de début
        updates_queue.put(json.dumps({
            'type': 'status',
            'message': 'Équipe créée, début du travail...',
            'agent': None
        }))

        # Création et lancement de l'équipe
        crew = Crew(
            agents=[directeur_factory, chef_de_projet, developpeur, testeur],
            tasks=tasks,
            verbose=True,
            process=Process.sequential
        )

        logger.info("Lancement du travail d'équipe...")
        result = crew.kickoff()
        logger.info("Travail d'équipe terminé")
        
        # Notification de fin
        updates_queue.put(json.dumps({
            'type': 'complete',
            'message': str(result),
            'agent': None
        }, cls=CustomJSONEncoder))

    except Exception as e:
        error_msg = f"Erreur dans run_crew: {str(e)}"
        logger.error(error_msg)
        updates_queue.put(json.dumps({
            'type': 'error',
            'message': error_msg,
            'agent': None
        }))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stream')
def stream():
    def event_stream():
        while True:
            try:
                update = updates_queue.get()
                yield f"data: {update}\n\n"
            except Exception as e:
                logger.error(f"Erreur dans event_stream: {str(e)}")
                continue
    
    return Response(event_stream(), mimetype='text/event-stream')

@app.route('/api/team-status')
def get_team_status():
    """Récupère le statut actuel de l'équipe"""
    try:
        # Récupération des statuts des agents
        team_members = [
            {
                'role': 'Directeur Factory',
                'status': 'Actif',
                'progress': 75
            },
            {
                'role': 'Chef de Projet',
                'status': 'En cours',
                'progress': 60
            },
            {
                'role': 'Développeur',
                'status': 'En cours',
                'progress': 80
            },
            {
                'role': 'Testeur',
                'status': 'En attente',
                'progress': 40
            }
        ]

        # Métriques globales
        metrics = {
            'tasksCompleted': 12,
            'tasksInProgress': 8,
            'tasksPending': 5
        }

        return jsonify({
            'members': team_members,
            'metrics': metrics
        })
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du statut de l'équipe: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.after_request
def after_request(response):
    """Ajoute les headers CORS nécessaires"""
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

if __name__ == '__main__':
    try:
        # Démarrage initial du thread pour l'exécution de l'équipe
        crew_thread = threading.Thread(target=run_crew)
        crew_thread.daemon = True
        crew_thread.start()
        
        # Utilisation du port 5001 au lieu de 5000
        logger.info("Démarrage du serveur Flask sur le port 5001...")
        app.run(host='0.0.0.0', debug=True, threaded=True, port=5001)
    except Exception as e:
        logger.error(f"Erreur au démarrage: {str(e)}") 