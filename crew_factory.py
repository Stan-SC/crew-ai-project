from crewai import Agent, Task, Crew
from dotenv import load_dotenv
import os

class CrewFactory:
    """
    Factory pour créer et gérer une équipe d'agents CrewAI.
    """
    
    def __init__(self, model="gpt-3.5-turbo", temperature=0.7):
        """
        Initialise la factory avec les paramètres par défaut.
        
        Args:
            model (str): Le modèle LLM à utiliser
            temperature (float): La température pour la génération de texte
        """
        load_dotenv()
        self.model = model
        self.temperature = temperature
        
    def create_agent(self, name, role, goal, backstory):
        """
        Crée un agent avec les paramètres spécifiés.
        """
        return Agent(
            name=name,
            role=role,
            goal=goal,
            backstory=backstory,
            allow_delegation=False,
            verbose=True,
            llm_config={
                "model": self.model,
                "temperature": self.temperature
            }
        )
    
    def create_task(self, description, expected_output, agent):
        """
        Crée une tâche avec les paramètres spécifiés.
        """
        return Task(
            description=description,
            expected_output=expected_output,
            agent=agent
        )
    
    def create_development_crew(self):
        """
        Crée une équipe de développement standard avec un chef de projet,
        un développeur et un testeur.
        """
        # Création des agents
        chef_de_projet = self.create_agent(
            name="Chef de Projet",
            role="Planifie les tâches et organise le travail d'équipe",
            goal="Créer un plan clair et efficace pour le développement",
            backstory="Expert en gestion de projet informatique avec 10 ans d'expérience et une capacité à améliorer les processus"
        )
        
        developpeur = self.create_agent(
            name="Développeur",
            role="Écrit du code Python propre et efficace",
            goal="Transformer les spécifications en code fonctionnel",
            backstory="Développeur Python senior avec expertise en bonnes pratiques"
        )
        
        testeur = self.create_agent(
            name="Testeur",
            role="Teste et améliore la qualité du code",
            goal="Assurer la qualité et la fiabilité du code",
            backstory="Expert en QA avec une forte attention aux détails"
        )
        
        # Création des tâches
        planification = self.create_task(
            description="Créer un plan détaillé pour le développement du projet",
            expected_output="Document détaillant les étapes, fonctionnalités et considérations techniques",
            agent=chef_de_projet
        )
        
        ecriture_code = self.create_task(
            description="Écrire le code selon les spécifications, incluant gestion des erreurs et documentation",
            expected_output="Code fonctionnel et documenté",
            agent=developpeur
        )
        
        test_code = self.create_task(
            description="Tester le code et suggérer des améliorations",
            expected_output="Rapport de tests avec cas testés et suggestions d'amélioration",
            agent=testeur
        )
        
        # Création de l'équipe
        return Crew(
            agents=[chef_de_projet, developpeur, testeur],
            tasks=[planification, ecriture_code, test_code],
            verbose=True
        )

# Exemple d'utilisation
if __name__ == "__main__":
    # Création d'une factory avec les paramètres par défaut
    factory = CrewFactory()
    
    # Création d'une équipe de développement
    equipe = factory.create_development_crew()
    
    # Lancement du travail d'équipe
    resultat = equipe.kickoff()
    print("\nRésultat final :")
    print(resultat) 