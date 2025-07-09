# Test API

Une API FastAPI pour la classification de requêtes et l'extraction d'informations à partir de textes via BoundaryML et des modèles de langage.  
Les modèles de langue sont hébergés sur [Nebius](https://nebius.com/) et nécessitent une clé API pour être utilisés.

## Fonctionnalités

- **Classification de requêtes** : Catégorise des requêtes textuelles selon des thèmes prédéfinis avec possibilité d'ajouter un score de confiance
- **Extraction d'informations** : Extrait des informations structurées à partir de textes (ex: CV, documents)
    - Le schéma de sorti peut être modifié dans app/data/completion_format.json

## Technologies utilisées

- **FastAPI** : Framework web moderne et rapide pour Python
- **BAML** : Framework pour l'intégration de modèles de langage
- **Pydantic** : Validation et sérialisation des données
- **Uvicorn** : Serveur ASGI pour FastAPI
- **UV** : Gestionnaire de paquets et d'environnements Python ultra-rapide

## Structure du projet

```
test_project/
├── app/
│   ├── __init__.py
│   ├── main.py              # Point d'entrée de l'API FastAPI
│   ├── schemas.py           # Modèles Pydantic pour la validation des données
│   ├── data/
│   │   └── completion_format.json  # Format de complétion pour l'extraction
│   └── services/
│       ├── categorize_query.py     # Service de classification
│       └── generate_form.py        # Service d'extraction d'informations
├── baml_src/
│   ├── categorize_query.baml       # Configuration BAML pour la classification
│   ├── clients.baml               # Configuration des clients BAML
│   ├── complete_form.baml         # Configuration BAML pour l'extraction
│   └── generators.baml            # Générateurs BAML
├── baml_client/               # Client BAML généré automatiquement
├── pyproject.toml           # Configuration du projet et dépendances
├── uv.lock                  # Fichier de verrouillage des dépendances UV
├── README.md               # Ce fichier
└──tests/
  ├── __init__.py
  ├── test_main.py           # Tests des endpoints FastAPI
  ├── test_schemas.py        # Tests des modèles Pydantic
  ├── test_services.py       # Tests des services métier
  └── test_performance.py    # Tests de performance et charge
```

## Installation et démarrage

### Prérequis

- Python 3.12 ou plus récent
- [UV](https://docs.astral.sh/uv/) installé sur votre système


### Configuration du projet

1. **Cloner ou naviguer vers le projet** :
   ```bash
    git clone https://github.com/settayeb/test_project
    cd test_project
   ```

2. **Installer les dépendances avec UV** :
   ```bash
   uv sync
   ```

3. **Générer les fichiers baml** :
    ```bash
    uv run baml-cli generate
    ```
4. **Configurer les variables d'environnement** :
   La variable environemental NEBIUS_API_KEY doit contenir votre clé API

    ```bash
    export NEBIUS_API_KEY=<YOUR_API_KEY>
    ```

### Démarrage de l'API

Pour démarrer l'API avec UV :

```bash
# Démarrage standard
uv run uvicorn app.main:app --reload

# Ou spécifier l'host et le port
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

L'API sera accessible à l'adresse : http://localhost:8000

### Documentation interactive

Une fois l'API démarrée, vous pouvez accéder à :
- **Documentation Swagger** : http://localhost:8000/docs
- **Documentation ReDoc** : http://localhost:8000/redoc

## Endpoints disponibles

### 1. Classification de requêtes

**POST** `/categorize/`

Catégorise une requête textuelle selon des thèmes prédéfinis.

**Corps de la requête** :
```json
{
    "text": "I am calling because I have a problem with my internet connection",
    "themes": [
        {
            "title": "Technical support",
            "description": "The customer is calling for technical support"
        },
        {
            "title": "Billing",
            "description": "The customer is calling for billing issues"
        },
        {
            "title": "Refund",
            "description": "The customer is calling for a refund"
        }
    ]
}
```

**Réponse** :
```json
{
    "model_reasoning": "This text is about technical support, therefore the chosen theme is 'Technical support'.",
    "chosen_theme": {
        "title": "Technical support",
        "description": "The customer is calling for technical support"
    }
}
```

**POST** `/categorize-score/`

Catégorise une requête textuelle selon des thèmes prédéfinis.

**Corps de la requête** :
```json
{
    "text": "I am calling because I have a problem with my internet connection. I want a refund",
    "themes": [
        {
            "title": "Technical support",
            "description": "The customer is calling for technical support"
        },
        {
            "title": "Billing",
            "description": "The customer is calling for billing issues"
        },
        {
            "title": "Refund",
            "description": "The customer is calling for a refund"
        }
    ]
}
```

**Réponse** :
```json
{
    "model_reasoning": "This text is about technical support, therefore the chosen theme is 'Technical support'.",
    "chosen_theme": {
        "title": "Technical support",
        "description": "The customer is calling for technical support"
    },
    "confidence": 0.6
}
```

### 2. Extraction d'informations

**POST** `/extract/`

Extrait des informations structurées à partir d'un texte.

**Corps de la requête** :
```json
{
  "text": "Texte à analyser (ex: contenu d'un CV)"
}
```

### 3. Extraction en streaming

**POST** `/stream-extract/`

Version streaming de l'extraction d'informations pour les documents volumineux.



## 🧪 Tests


### Lancement des tests

```bash
# Tous les tests
uv run pytest
```

### Types de tests disponibles

- **Tests unitaires** : Validation des fonctions individuelles
- **Tests d'intégration** : Tests de bout en bout avec mocks
- **Tests de performance** : Temps de réponse et charge
- **Tests de schémas** : Validation des modèles Pydantic

## Améliorations:

- Rajouter les test de services
- Gérer la configuration des différents paramètres de l'API
- Implémenter la possibilité de changer de modèle
- Intégrer une pipe d'évaluation des modèles avec un dataset de jeu.
- Augmenter la robustesse et gérer les cas particuliers(exemple: Aucun thème n'est donné en entrée pour la catégorisation)
