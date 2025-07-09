import pytest
from unittest.mock import Mock, patch, AsyncMock
import json
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.main import app
from app.schemas import ClassificationInput, ClassificationClass, ExtractionInput


@pytest.fixture
def client():
    """Fixture pour le client de test FastAPI."""
    return TestClient(app)


@pytest.fixture
def mock_completion_form():
    """Fixture pour le format de complétion mocké."""
    return {
        "title": "Customer Information Form",
        "type": "object",
        "properties": {
            "personal_info": {
                "type": "object",
                "properties": {
                    "first_name": {"type": "string", "description": "First name"},
                    "last_name": {"type": "string", "description": "Last name"}
                }
            }
        }
    }


@pytest.fixture
def sample_classification_input():
    """Fixture pour les données de classification."""
    return {
        "text": "J'aimerais souscrire à une assurance vie",
        "themes": [
            {
                "title": "Assurance",
                "description": "Questions relatives aux assurances"
            },
            {
                "title": "Finance",
                "description": "Questions financières"
            }
        ]
    }


@pytest.fixture
def sample_extraction_input():
    """Fixture pour les données d'extraction."""
    return {
        "text": "Jean Dupont, 30 ans, ingénieur logiciel chez TechCorp"
    }


class TestMainEndpoints:
    """Tests pour les endpoints principaux de l'API."""

    @patch('app.main.categorize_query')
    @patch('app.main.Collector')
    @patch('app.main.ClientRegistry')
    def test_categorize_endpoint(self, mock_registry, mock_collector, mock_categorize, client, sample_classification_input):
        """Test de l'endpoint /categorize/."""
        # Mock des retours
        mock_categorize.return_value = {"category": "Assurance", "confidence": 0.85}
        
        response = client.post("/categorize/", json=sample_classification_input)
        
        assert response.status_code == 200
        data = response.json()
        assert "category" in data
        assert "confidence" in data
        mock_categorize.assert_called_once()

    @patch('app.main.categorize_with_confidence')
    @patch('app.main.Collector')
    @patch('app.main.ClientRegistry')
    def test_categorize_score_endpoint(self, mock_registry, mock_collector, mock_categorize_conf, client, sample_classification_input):
        """Test de l'endpoint /categorize-score/."""
        # Mock des retours
        mock_categorize_conf.return_value = {"category": "Assurance", "confidence": 0.92}
        
        response = client.post("/categorize-score/?n=5", json=sample_classification_input)
        
        assert response.status_code == 200
        data = response.json()
        assert "category" in data
        assert "confidence" in data
        mock_categorize_conf.assert_called_once()

    @patch('app.main.fill_form')
    @patch('app.main.Collector')
    @patch('app.main.ClientRegistry')
    @patch('builtins.open', create=True)
    @patch('app.main.json.load')
    def test_extract_endpoint(self, mock_json_load, mock_open, mock_registry, mock_collector, 
                             mock_fill_form, client, sample_extraction_input, mock_completion_form):
        """Test de l'endpoint /extract/."""
        # Mock des retours
        mock_json_load.return_value = mock_completion_form
        mock_fill_form.return_value = {
            "personal_info": {
                "first_name": "Jean",
                "last_name": "Dupont"
            }
        }
        
        response = client.post("/extract/", json=sample_extraction_input)
        
        assert response.status_code == 200
        data = response.json()
        assert "personal_info" in data
        mock_fill_form.assert_called_once()

    @patch('app.main.stream_fill_form')
    @patch('app.main.Collector')
    @patch('app.main.ClientRegistry')
    @patch('builtins.open', create=True)
    @patch('app.main.json.load')
    def test_stream_extract_endpoint(self, mock_json_load, mock_open, mock_registry, mock_collector,
                                   mock_stream_fill, client, sample_extraction_input, mock_completion_form):
        """Test de l'endpoint /stream-extract/."""
        # Mock des retours
        mock_json_load.return_value = mock_completion_form
        mock_stream_fill.return_value = iter([b'{"chunk": 1}', b'{"chunk": 2}'])
        
        response = client.post("/stream-extract/", json=sample_extraction_input)
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
        mock_stream_fill.assert_called_once()

    def test_invalid_classification_input(self, client):
        """Test avec des données de classification invalides."""
        invalid_data = {
            "text": "Test",
            # themes manquant
        }
        
        response = client.post("/categorize/", json=invalid_data)
        assert response.status_code == 422  # Validation error

    def test_invalid_extraction_input(self, client):
        """Test avec des données d'extraction invalides."""
        invalid_data = {
            # text manquant
        }
        
        response = client.post("/extract/", json=invalid_data)
        assert response.status_code == 422  # Validation error

    def test_empty_themes_list(self, client):
        """Test avec une liste de thèmes vide."""
        data = {
            "text": "Test text",
            "themes": []
        }
        
        response = client.post("/categorize/", json=data)
        # Devrait passer la validation mais pourrait retourner une erreur métier
        assert response.status_code in [200, 400, 422]

    @patch('app.main.categorize_query')
    @patch('app.main.Collector')
    @patch('app.main.ClientRegistry')
    def test_categorize_with_complex_themes(self, mock_registry, mock_collector, mock_categorize, client):
        """Test avec des thèmes complexes."""
        mock_categorize.return_value = {"category": "Assurance Auto", "confidence": 0.78}
        
        complex_data = {
            "text": "Mon véhicule a été endommagé dans un accident",
            "themes": [
                {
                    "title": "Assurance Auto",
                    "description": "Questions relatives à l'assurance automobile"
                },
                {
                    "title": "Assurance Habitation", 
                    "description": "Questions relatives à l'assurance habitation"
                },
                {
                    "title": "Sinistres",
                    "description": "Déclaration et gestion des sinistres"
                }
            ]
        }
        
        response = client.post("/categorize/", json=complex_data)
        assert response.status_code == 200
        data = response.json()
        assert data["category"] == "Assurance Auto"


class TestDataValidation:
    """Tests pour la validation des données."""

    def test_classification_input_validation(self):
        """Test de validation du modèle ClassificationInput."""
        # Test avec des données valides
        valid_data = {
            "text": "Test text",
            "themes": [
                {"title": "Theme1", "description": "Description1"}
            ]
        }
        classification_input = ClassificationInput(**valid_data)
        assert classification_input.text == "Test text"
        assert len(classification_input.themes) == 1

    def test_classification_class_validation(self):
        """Test de validation du modèle ClassificationClass."""
        # Test avec des données valides
        valid_data = {"title": "Test Title", "description": "Test Description"}
        classification_class = ClassificationClass(**valid_data)
        assert classification_class.title == "Test Title"
        assert classification_class.description == "Test Description"

    def test_extraction_input_validation(self):
        """Test de validation du modèle ExtractionInput."""
        # Test avec des données valides
        valid_data = {"text": "Test extraction text"}
        extraction_input = ExtractionInput(**valid_data)
        assert extraction_input.text == "Test extraction text"

    def test_classification_input_missing_fields(self):
        """Test de validation avec des champs manquants."""
        with pytest.raises(ValueError):
            ClassificationInput(text="Test")  # themes manquant

    def test_extraction_input_missing_fields(self):
        """Test de validation avec des champs manquants."""
        with pytest.raises(ValueError):
            ExtractionInput()  # text manquant



