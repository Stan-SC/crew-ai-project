"""
Configuration pour les tests pytest.
"""

import pytest
from crew_server import app

@pytest.fixture
def client():
    """Fixture pour créer un client de test."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def runner():
    """Fixture pour créer un runner de commandes CLI."""
    return app.test_cli_runner() 