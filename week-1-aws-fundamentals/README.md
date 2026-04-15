# Week 1 — AWS Fundamentals pour GenAI

## Objectifs d'apprentissage

- Comprendre les services AWS de base utilisés dans les architectures GenAI
- Créer et tester une Lambda Python avec API Gateway
- Manipuler S3 (lecture/écriture) — fondation du RAG en week 3
- Appliquer les bonnes pratiques IAM (least privilege)
- Déployer avec AWS SAM (Infrastructure as Code)

## Structure du projet

```
week-1-aws-fundamentals/
├── src/
│   ├── __init__.py
│   ├── lambda_function.py      # Lambda handler (AWS Lambda Powertools + Router)
│   └── ...
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── conftest.py          # Fixtures partagées (env, events, helpers)
│   │   ├── test_hello.py        # Tests endpoint /hello
│   │   └── test_s3.py           # Tests endpoints S3
│   └── integration/
│       ├── __init__.py
│       └── test_deployed_stack.py  # Tests sur stack déployé (skippés par défaut)
├── scripts/
│   ├── s3_operations.py         # Exercice standalone : opérations S3 avec boto3
│   └── README.md
├── events/
│   ├── hello_get.json           # Event GET /hello
│   ├── s3_list.json             # Event GET /s3/list
│   └── s3_put.json              # Event POST /s3/put
├── .gitignore
├── pyproject.toml               # Metadata projet + config pytest/ruff
├── samconfig.toml               # Config déploiement SAM
├── template.yaml                # SAM template (Lambda + API GW + S3 bucket)
├── requirements.txt             # Dépendances production (Lambda runtime)
├── requirements-dev.txt         # Dépendances dev/test
├── ARCHITECTURE.md              # Guide des décisions d'architecture
└── README.md
```

## Prérequis

- Python 3.12+
- AWS CLI configuré (`aws configure`)
- AWS SAM CLI (`pip install aws-sam-cli`)
- Un compte AWS avec accès à Bedrock (pour la week 2)

## Installation

```bash
cd week-1-aws-fundamentals
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# Production dependencies only (for deploying the Lambda)
pip install -r requirements.txt

# Development dependencies (for local testing)
pip install -r requirements-dev.txt
```

## Lancer les tests

```bash
# Tests unitaires uniquement (défaut — les tests d'intégration sont exclus)
pytest

# Tests unitaires avec couverture
pytest --cov=src

# Tests d'intégration (nécessite un stack déployé)
API_ENDPOINT=https://xxx.execute-api.us-east-1.amazonaws.com/Prod S3_BUCKET=genai-prep-dev-xxx pytest -m integration
```

## Tester localement avec SAM

```bash
# Démarrer l'API locale
sam local start-api

# Tester les endpoints
curl http://127.0.0.1:3000/hello?name=Apprenti
curl http://127.0.0.1:3000/s3/list?bucket=mon-bucket
```

## Déployer sur AWS

```bash
sam build
sam deploy --guided
```

Lors du premier déploiement, SAM demandera les paramètres (stack name, region, etc.).

## Endpoints de l'API

| Méthode | Path | Description |
|---------|------|-------------|
| GET | `/hello?name=X` | Retourne un message de bienvenue |
| GET | `/s3/list?bucket=X&prefix=Y` | Liste les objets S3 |
| POST | `/s3/put` | Écrit un objet S3 (body JSON: bucket, key, content) |

## Exercice S3 standalone

```bash
# Créer un bucket
python scripts/s3_operations.py --bucket genai-prep-dev-ACCOUNT_ID --action create-bucket

# Upload un fichier
python scripts/s3_operations.py --bucket genai-prep-dev-ACCOUNT_ID --action upload --key data/test.txt --file ./README.md

# Lister les objets
python scripts/s3_operations.py --bucket genai-prep-dev-ACCOUNT_ID --action list
```

Voir [scripts/README.md](scripts/README.md) pour plus de détails.

## Concepts clés pour l'examen

| Concept | Ce qu'il faut retenir |
|---------|----------------------|
| **Lambda** | Serverless, event-driven, pay-per-use. Handler = point d'entrée. |
| **API Gateway** | Expose Lambda via HTTP. REST ou HTTP API. |
| **S3** | Stockage objet. Utilisé pour les documents dans les architectures RAG. |
| **IAM** | Least privilege. Roles > Users pour les services. |
| **SAM** | Extension de CloudFormation pour serverless. `sam local` pour tester. |
| **Bedrock** | Service managé pour les modèles fondation (Claude, Titan, etc.). |

## Transition vers Week 2

La policy IAM inclut déjà les permissions `bedrock:InvokeModel`. En week 2, on ajoutera
l'appel à un modèle Bedrock directement depuis la Lambda.
