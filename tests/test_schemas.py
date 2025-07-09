import pytest
from pydantic import ValidationError
from app.schemas import ClassificationClass, ClassificationInput, ExtractionInput


class TestSchemas:
    """Tests pour les modèles de données Pydantic."""

    def test_classification_class_valid(self):
        """Test de création d'un ClassificationClass valide."""
        data = {
            "title": "Assurance",
            "description": "Questions relatives aux assurances"
        }
        
        classification_class = ClassificationClass(**data)
        
        assert classification_class.title == "Assurance"
        assert classification_class.description == "Questions relatives aux assurances"

    def test_classification_class_missing_title(self):
        """Test de ClassificationClass sans titre."""
        data = {
            "description": "Questions relatives aux assurances"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ClassificationClass(**data)
        
        assert "title" in str(exc_info.value)

    def test_classification_class_missing_description(self):
        """Test de ClassificationClass sans description."""
        data = {
            "title": "Assurance"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ClassificationClass(**data)
        
        assert "description" in str(exc_info.value)

    def test_classification_class_empty_strings(self):
        """Test de ClassificationClass avec des chaînes vides."""
        data = {
            "title": "",
            "description": ""
        }
        
        # Les chaînes vides sont techniquement valides en Pydantic
        classification_class = ClassificationClass(**data)
        assert classification_class.title == ""
        assert classification_class.description == ""

    def test_classification_input_valid(self):
        """Test de création d'un ClassificationInput valide."""
        data = {
            "text": "J'aimerais souscrire à une assurance",
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
        
        classification_input = ClassificationInput(**data)
        
        assert classification_input.text == "J'aimerais souscrire à une assurance"
        assert len(classification_input.themes) == 2
        assert classification_input.themes[0].title == "Assurance"
        assert classification_input.themes[1].title == "Finance"

    def test_classification_input_missing_text(self):
        """Test de ClassificationInput sans texte."""
        data = {
            "themes": [
                {
                    "title": "Assurance",
                    "description": "Questions relatives aux assurances"
                }
            ]
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ClassificationInput(**data)
        
        assert "text" in str(exc_info.value)

    def test_classification_input_missing_themes(self):
        """Test de ClassificationInput sans thèmes."""
        data = {
            "text": "J'aimerais souscrire à une assurance"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ClassificationInput(**data)
        
        assert "themes" in str(exc_info.value)

    def test_classification_input_empty_themes_list(self):
        """Test de ClassificationInput avec une liste de thèmes vide."""
        data = {
            "text": "J'aimerais souscrire à une assurance",
            "themes": []
        }
        
        # Une liste vide est techniquement valide
        classification_input = ClassificationInput(**data)
        assert len(classification_input.themes) == 0

    def test_classification_input_invalid_theme(self):
        """Test de ClassificationInput avec un thème invalide."""
        data = {
            "text": "J'aimerais souscrire à une assurance",
            "themes": [
                {
                    "title": "Assurance"
                    # description manquante
                }
            ]
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ClassificationInput(**data)
        
        assert "description" in str(exc_info.value)

    def test_extraction_input_valid(self):
        """Test de création d'un ExtractionInput valide."""
        data = {
            "text": "Jean Dupont, 30 ans, ingénieur logiciel"
        }
        
        extraction_input = ExtractionInput(**data)
        
        assert extraction_input.text == "Jean Dupont, 30 ans, ingénieur logiciel"

    def test_extraction_input_missing_text(self):
        """Test de ExtractionInput sans texte."""
        data = {}
        
        with pytest.raises(ValidationError) as exc_info:
            ExtractionInput(**data)
        
        assert "text" in str(exc_info.value)

    def test_extraction_input_empty_text(self):
        """Test de ExtractionInput avec texte vide."""
        data = {
            "text": ""
        }
        
        # Un texte vide est techniquement valide
        extraction_input = ExtractionInput(**data)
        assert extraction_input.text == ""

    def test_classification_input_with_multiple_themes(self):
        """Test avec plusieurs thèmes complexes."""
        data = {
            "text": "Mon véhicule a été endommagé et j'aimerais déclarer un sinistre",
            "themes": [
                {
                    "title": "Assurance Auto",
                    "description": "Questions relatives à l'assurance automobile et aux véhicules"
                },
                {
                    "title": "Sinistres",
                    "description": "Déclaration et gestion des sinistres"
                },
                {
                    "title": "Indemnisation",
                    "description": "Processus d'indemnisation et remboursements"
                }
            ]
        }
        
        classification_input = ClassificationInput(**data)
        
        assert len(classification_input.themes) == 3
        assert all(theme.title and theme.description for theme in classification_input.themes)

    def test_classification_input_with_long_text(self):
        """Test avec un texte très long."""
        long_text = "Lorem ipsum " * 1000  # Texte très long
        
        data = {
            "text": long_text,
            "themes": [
                {
                    "title": "Test",
                    "description": "Test description"
                }
            ]
        }
        
        classification_input = ClassificationInput(**data)
        assert len(classification_input.text) > 10000

    def test_extraction_input_with_long_text(self):
        """Test d'extraction avec un texte très long."""
        long_text = "Jean Dupont " * 1000  # Texte très long
        
        data = {
            "text": long_text
        }
        
        extraction_input = ExtractionInput(**data)
        assert len(extraction_input.text) > 10000

    def test_schemas_json_serialization(self):
        """Test de sérialisation JSON des schémas."""
        classification_class = ClassificationClass(
            title="Assurance",
            description="Questions relatives aux assurances"
        )
        
        # Test de sérialisation
        json_data = classification_class.model_dump()
        assert json_data["title"] == "Assurance"
        assert json_data["description"] == "Questions relatives aux assurances"
        
        # Test de désérialisation
        new_class = ClassificationClass(**json_data)
        assert new_class.title == classification_class.title
        assert new_class.description == classification_class.description
