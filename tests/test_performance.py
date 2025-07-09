import pytest
import asyncio
import time
from unittest.mock import patch, Mock, AsyncMock
from fastapi.testclient import TestClient
from app.main import app


class TestPerformance:
    """Tests de performance pour l'API."""

    @pytest.fixture
    def client(self):
        """Client de test."""
        return TestClient(app)

    @pytest.fixture
    def sample_data(self):
        """Données de test."""
        return {
            "classification_input": {
                "text": "Test de performance pour la classification",
                "themes": [
                    {"title": "Test", "description": "Description de test"}
                ]
            },
            "extraction_input": {
                "text": "Test de performance pour l'extraction"
            }
        }

    @patch('app.main.categorize_query')
    @patch('app.main.Collector')
    @patch('app.main.ClientRegistry')
    def test_categorize_response_time(self, mock_registry, mock_collector, mock_categorize, client, sample_data):
        """Test du temps de réponse de l'endpoint de catégorisation."""
        mock_categorize.return_value = {"category": "Test", "confidence": 0.9}
        
        start_time = time.time()
        response = client.post("/categorize/", json=sample_data["classification_input"])
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 2.0  # Le endpoint doit répondre en moins de 2 secondes

    @patch('app.main.fill_form')
    @patch('app.main.Collector')
    @patch('app.main.ClientRegistry')
    @patch('builtins.open', create=True)
    @patch('app.main.json.load')
    def test_extract_response_time(self, mock_json_load, mock_open, mock_registry, 
                                  mock_collector, mock_fill_form, client, sample_data):
        """Test du temps de réponse de l'endpoint d'extraction."""
        mock_json_load.return_value = {"test": "format"}
        mock_fill_form.return_value = {"result": "test"}
        
        start_time = time.time()
        response = client.post("/extract/", json=sample_data["extraction_input"])
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 3.0  # L'extraction peut prendre un peu plus de temps

    @patch('app.main.categorize_query')
    @patch('app.main.Collector')
    @patch('app.main.ClientRegistry')
    def test_concurrent_requests(self, mock_registry, mock_collector, mock_categorize, client, sample_data):
        """Test de requêtes concurrentes."""
        mock_categorize.return_value = {"category": "Test", "confidence": 0.9}
        
        import concurrent.futures
        import threading
        
        def make_request():
            return client.post("/categorize/", json=sample_data["classification_input"])
        
        start_time = time.time()
        
        # Faire 10 requêtes concurrentes
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            responses = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Toutes les requêtes doivent réussir
        assert all(response.status_code == 200 for response in responses)
        
        # Le temps total ne doit pas être excessif
        assert total_time < 10.0

    def test_large_text_processing(self, client):
        """Test avec un texte très volumineux."""
        # Créer un texte de 10KB
        large_text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 200
        
        large_data = {
            "text": large_text,
            "themes": [
                {"title": "Test", "description": "Description de test"}
            ]
        }
        
        with patch('app.main.categorize_query') as mock_categorize, \
             patch('app.main.Collector'), \
             patch('app.main.ClientRegistry'):
            
            mock_categorize.return_value = {"category": "Test", "confidence": 0.9}
            
            start_time = time.time()
            response = client.post("/categorize/", json=large_data)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            assert response.status_code == 200
            assert response_time < 5.0  # Même avec un gros texte, pas plus de 5 secondes

    def test_many_themes_processing(self, client):
        """Test avec beaucoup de thèmes."""
        # Créer 50 thèmes
        many_themes = [
            {"title": f"Theme{i}", "description": f"Description du thème {i}"}
            for i in range(50)
        ]
        
        data = {
            "text": "Test avec beaucoup de thèmes",
            "themes": many_themes
        }
        
        with patch('app.main.categorize_query') as mock_categorize, \
             patch('app.main.Collector'), \
             patch('app.main.ClientRegistry'):
            
            mock_categorize.return_value = {"category": "Theme1", "confidence": 0.9}
            
            start_time = time.time()
            response = client.post("/categorize/", json=data)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            assert response.status_code == 200
            assert response_time < 3.0


class TestLoadTesting:
    """Tests de charge pour évaluer la capacité de l'API."""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_sequential_load(self, client):
        """Test de charge séquentielle."""
        with patch('app.main.categorize_query') as mock_categorize, \
             patch('app.main.Collector'), \
             patch('app.main.ClientRegistry'):
            
            mock_categorize.return_value = {"category": "Test", "confidence": 0.9}
            
            data = {
                "text": "Test de charge",
                "themes": [{"title": "Test", "description": "Test description"}]
            }
            
            # Faire 100 requêtes séquentielles
            response_times = []
            success_count = 0
            
            for i in range(100):
                start_time = time.time()
                response = client.post("/categorize/", json=data)
                end_time = time.time()
                
                response_times.append(end_time - start_time)
                if response.status_code == 200:
                    success_count += 1
            
            # Vérifications
            assert success_count == 100  # Toutes les requêtes doivent réussir
            
            # Temps de réponse moyen
            avg_response_time = sum(response_times) / len(response_times)
            assert avg_response_time < 1.0
            
            # 95e percentile
            response_times.sort()
            p95_response_time = response_times[int(0.95 * len(response_times))]
            assert p95_response_time < 2.0

    def test_memory_usage(self, client):
        """Test d'utilisation mémoire lors de requêtes répétées."""
        import psutil
        import os
        
        with patch('app.main.categorize_query') as mock_categorize, \
             patch('app.main.Collector'), \
             patch('app.main.ClientRegistry'):
            
            mock_categorize.return_value = {"category": "Test", "confidence": 0.9}
            
            data = {
                "text": "Test d'utilisation mémoire",
                "themes": [{"title": "Test", "description": "Test description"}]
            }
            
            # Mesurer la mémoire initiale
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Faire plusieurs requêtes
            for i in range(50):
                response = client.post("/categorize/", json=data)
                assert response.status_code == 200
            
            # Mesurer la mémoire finale
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            # La consommation mémoire ne doit pas exploser
            assert memory_increase < 100  # Moins de 100MB d'augmentation

