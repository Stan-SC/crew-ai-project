"""
Tests unitaires pour le serveur CrewAI.
"""

import unittest
import json
from unittest.mock import patch
from crewai import Agent
from crew_server import app, FactoryConfig, QueueManager, TaskConfig, MAX_QUEUE_SIZE

class TestCrewServer(unittest.TestCase):
    """Tests pour le serveur CrewAI"""

    def setUp(self):
        """Configuration initiale pour les tests"""
        self.app = app.test_client()
        self.app.testing = True
        self.test_agent = Agent(
            name="Test Agent",
            role="Test Role",
            goal="Test Goal",
            backstory="Test Backstory"
        )

    def test_factory_config_validation(self):
        """Test de la validation de la configuration du Factory"""
        # Test avec des valeurs valides
        try:
            config = FactoryConfig(
                goal="Test goal",
                backstory="Test backstory"
            )
            self.assertEqual(config.goal, "Test goal")
            self.assertEqual(config.backstory, "Test backstory")
        except ValueError:
            self.fail("FactoryConfig a levé une ValueError inattendue")

        # Test avec des valeurs invalides
        with self.assertRaises(ValueError):
            FactoryConfig(goal="", backstory="Test")
        with self.assertRaises(ValueError):
            FactoryConfig(goal="Test", backstory="")
        with self.assertRaises(ValueError):
            FactoryConfig(goal=None, backstory="Test")

    def test_queue_manager(self):
        """Test du gestionnaire de queue"""
        queue_manager = QueueManager(maxsize=3)

        # Test d'ajout d'éléments
        queue_manager.put({"test": 1})
        queue_manager.put({"test": 2})
        queue_manager.put({"test": 3})

        # Vérification de la taille maximale
        queue_manager.put({"test": 4})  # Devrait supprimer le plus ancien élément
        self.assertEqual(queue_manager.get()["test"], 2)

        # Test de la méthode clear
        queue_manager.clear()
        with self.assertRaises(queue.Empty):
            queue_manager.queue.get_nowait()

    def test_update_factory_goal_validation(self):
        """Test de la validation de la mise à jour de l'objectif du Factory"""
        # Test avec un objectif manquant
        response = self.app.post('/update_factory_goal',
                               data=json.dumps({}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertFalse(json.loads(response.data)['success'])

    @patch('crew_server.restart_crew')
    def test_update_factory_goal_restarts_crew(self, mock_restart):
        """Test que la mise à jour de l'objectif redémarre l'équipe"""
        response = self.app.post('/update_factory_goal',
                               data=json.dumps({'goal': 'Nouveau test goal'}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json.loads(response.data)['success'])
        mock_restart.assert_called_once()

    def test_update_factory_backstory_validation(self):
        """Test de la validation de la mise à jour de l'histoire du Factory"""
        # Test avec une histoire manquante
        response = self.app.post('/update_factory_backstory',
                               data=json.dumps({}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertFalse(json.loads(response.data)['success'])

    @patch('crew_server.restart_crew')
    def test_update_factory_backstory_restarts_crew(self, mock_restart):
        """Test que la mise à jour de l'histoire redémarre l'équipe"""
        response = self.app.post('/update_factory_backstory',
                               data=json.dumps({'backstory': 'Nouvelle histoire test'}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json.loads(response.data)['success'])
        mock_restart.assert_called_once()

    def test_get_factory_config(self):
        """Test de la récupération de la configuration du Factory"""
        response = self.app.get('/get_factory_config')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('goal', data)
        self.assertIn('backstory', data)

    def test_restart_crew(self):
        """Test du redémarrage de l'équipe"""
        response = self.app.post('/restart_crew')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json.loads(response.data)['success'])

    def test_task_config_validation(self):
        """Test de la validation de la configuration des tâches"""
        # Test avec des valeurs valides
        try:
            config = TaskConfig(
                description="Test description",
                expected_output="Test output",
                agent=self.test_agent
            )
            self.assertEqual(config.description, "Test description")
            self.assertEqual(config.expected_output, "Test output")
            self.assertEqual(config.agent, self.test_agent)
        except ValueError:
            self.fail("TaskConfig a levé une ValueError inattendue")

        # Test avec des valeurs invalides
        with self.assertRaises(ValueError):
            TaskConfig(description="", expected_output="Test", agent=self.test_agent)
        with self.assertRaises(ValueError):
            TaskConfig(description="Test", expected_output="", agent=self.test_agent)
        with self.assertRaises(ValueError):
            TaskConfig(description="Test", expected_output="Test", agent=None)
        with self.assertRaises(ValueError):
            TaskConfig(description=None, expected_output="Test", agent=self.test_agent)

if __name__ == '__main__':
    unittest.main() 