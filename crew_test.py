from crewai import Agent, Task, Crew
from dotenv import load_dotenv
import os

# Chargement des variables d'environnement
load_dotenv()

# Configuration des agents avec GPT-3.5-turbo
chef_de_projet = Agent(
    name="Chef de Projet",
    role="Planifie les tâches et organise le travail d'équipe",
    goal="Créer un plan clair et efficace pour le développement",
    backstory="Expert en gestion de projet avec 10 ans d'expérience",
    allow_delegation=False,
    verbose=True,
    llm_config={
        "model": "gpt-3.5-turbo",
        "temperature": 0.7
    }
)

developpeur = Agent(
    name="Développeur",
    role="Écrit du code Python propre et efficace",
    goal="Transformer les spécifications en code fonctionnel",
    backstory="Développeur Python senior avec expertise en bonnes pratiques",
    allow_delegation=False,
    verbose=True,
    llm_config={
        "model": "gpt-3.5-turbo",
        "temperature": 0.7
    }
)

testeur = Agent(
    name="Testeur",
    role="Teste et améliore la qualité du code",
    goal="Assurer la qualité et la fiabilité du code",
    backstory="Expert en QA avec une forte attention aux détails",
    allow_delegation=False,
    verbose=True,
    llm_config={
        "model": "gpt-3.5-turbo",
        "temperature": 0.7
    }
)

# Définition des tâches avec plus de détails
planification = Task(
    description="Créer un plan détaillé pour un script Python qui calcule la factorielle d'un nombre",
    expected_output="Un document détaillant les étapes de développement, les fonctionnalités requises et les considérations techniques",
    agent=chef_de_projet
)

ecriture_code = Task(
    description="Écrire le code Python pour calculer la factorielle, en incluant la gestion des erreurs et la documentation",
    expected_output="Code Python fonctionnel et documenté pour calculer la factorielle d'un nombre",
    agent=developpeur
)

test_code = Task(
    description="Tester le code avec différents cas d'utilisation et suggérer des améliorations",
    expected_output="Rapport de tests détaillé avec les cas testés et les suggestions d'amélioration",
    agent=testeur
)

# Création de l'équipe
equipe = Crew(
    agents=[chef_de_projet, developpeur, testeur],
    tasks=[planification, ecriture_code, test_code],
    verbose=True
)

# Exécution
resultat = equipe.kickoff()
print("\nRésultat final :")
print(resultat) 