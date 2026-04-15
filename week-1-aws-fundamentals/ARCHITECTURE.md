# Week 1 — Guide des décisions d'architecture

Ce document explique **chaque choix** fait dans la structure du projet Week 1.
L'objectif : tu peux reproduire cette approche sur n'importe quel projet serverless AWS.

---

## 1. Objectif global de la Week 1

Construire un projet Lambda fonctionnel de bout en bout — pas juste un "Hello World" jetable,
mais une base qui ressemble à ce qu'on livre en production. Ça couvre :

- **Lambda** : compute serverless, le moteur de 90% des architectures GenAI sur AWS
- **API Gateway** : exposer la Lambda en HTTP (c'est comme ça qu'un front/client consomme un modèle)
- **S3** : stockage objet — en week 3 (RAG), les documents iront dans S3
- **IAM** : sécurité — sans ça, rien ne tourne sur AWS
- **SAM** : Infrastructure as Code — déployer en un `sam deploy`, pas à la main dans la console

Chaque service est un building block qui sera réutilisé dans les semaines suivantes.

---

## 2. Pourquoi cette structure de dossiers

```
week-1-aws-fundamentals/
├── src/                  # Code applicatif (Lambda)
├── tests/                # Tests (unit + integration)
├── events/               # Payloads de test pour SAM/Lambda
├── scripts/              # Outils CLI / exercices hors Lambda
├── template.yaml         # Infrastructure as Code (SAM)
├── pyproject.toml        # Config projet Python
├── samconfig.toml        # Config déploiement SAM
├── requirements.txt      # Dépendances production (Lambda)
├── requirements-dev.txt  # Dépendances dev/tests (local)
└── .gitignore            # Fichiers à exclure de git
```

### Principe : séparation des responsabilités

Chaque dossier a **un seul rôle**. Quand tu cherches quelque chose, tu sais où regarder.
C'est le même principe qu'en code (Single Responsibility) appliqué à l'arborescence.

| Dossier | Responsabilité | Qui y touche |
|---------|---------------|-------------|
| `src/` | Code métier uniquement | Le développeur |
| `tests/` | Validation du code | Le développeur + la CI |
| `events/` | Données de test | Le développeur + SAM CLI |
| `scripts/` | Exercices CLI / outils dev | Le développeur |
| Racine | Config projet (SAM, Python, git) | Setup initial |

---

## 3. `src/` — Pourquoi isoler le code applicatif

```
src/
├── __init__.py
└── lambda_function.py
```

### Pourquoi pas le code à la racine ?

- SAM a besoin d'un `CodeUri` dans le template → on pointe vers `src/`
- Quand SAM package la Lambda, il prend **tout le contenu** du dossier `CodeUri`. Si le code
  est à la racine, SAM embarquerait aussi les tests, les events, le README, etc.
- Isolation = la Lambda déployée contient uniquement ce dont elle a besoin

### Pourquoi `__init__.py` ?

- Fait de `src/` un **package Python** valide
- Permet les imports propres dans les tests : `from lambda_function import lambda_handler`
- Sans ça, pytest et les IDE ont des problèmes de résolution d'imports

### Pourquoi `lambda_function.py` comme nom ?

- C'est la **convention AWS Lambda** : le handler par défaut est `lambda_function.lambda_handler`
- Si tu changes le nom, il faut aussi changer le `Handler` dans le template SAM
- Garder la convention = moins de config = moins de bugs

### Pourquoi les scripts CLI sont dans `scripts/` et pas `src/` ?

- `scripts/s3_operations.py` est un **exercice standalone** pour pratiquer S3 en dehors de Lambda
- SAM embarque tout `src/` dans le package Lambda → un script CLI dedans = poids mort en production
- En production, on aurait un `utils/` ou `services/` pour la logique partagée

---

## 4. `tests/` — Pourquoi unit et integration séparés

```
tests/
├── __init__.py
├── unit/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_hello.py
│   └── test_s3.py
└── integration/
    ├── __init__.py
    └── test_deployed_stack.py
```

### Deux types de tests, deux vitesses

| Type | Vitesse | Dépendance AWS | Quand les lancer |
|------|---------|---------------|-----------------|
| **Unit** | ~1 seconde | Aucune (moto simule AWS) | A chaque changement de code |
| **Integration** | ~5-10 secondes | Stack déployé obligatoire | Avant un merge / en CI |

### Pourquoi les séparer physiquement ?

```toml
# pyproject.toml
addopts = "-m 'not integration'"
```

- Par défaut, `pytest` ne lance que les tests unitaires
- Les tests d'intégration nécessitent un stack AWS réel → on ne veut pas qu'ils cassent en local
- Le marqueur `@pytest.mark.integration` + le filtre dans `pyproject.toml` gèrent ça automatiquement

### Pourquoi `conftest.py` ?

C'est le fichier magique de pytest — les fixtures définies dedans sont **automatiquement
disponibles** dans tous les tests du même dossier (et sous-dossiers).

```python
# conftest.py — chargé automatiquement par pytest
@pytest.fixture(autouse=True)
def set_env(monkeypatch):
    monkeypatch.setenv("S3_BUCKET", BUCKET_NAME)
```

Avantages :
- **DRY** : les fixtures ne sont écrites qu'une fois
- **`autouse=True`** : `set_env` s'applique à TOUS les tests sans qu'on le passe en argument
- **`monkeypatch`** : modifie les variables d'env temporairement (restaure après chaque test)

### Pourquoi un fichier de test par domaine (`test_hello.py`, `test_s3.py`) ?

- **Lisibilité** : quand un test S3 échoue, tu ouvres `test_s3.py`, pas un fichier de 200 lignes
- **Parallélisation** : pytest-xdist peut lancer `test_hello.py` et `test_s3.py` en parallèle
- **Historique git** : les changements sur les tests S3 n'apparaissent pas dans l'historique des tests hello

### Pourquoi `moto` (et pas des mocks manuels) ?

```python
from moto import mock_aws

@mock_aws
def test_s3_list():
    s3 = boto3.client("s3")          # ← C'est un VRAI appel boto3
    s3.create_bucket(Bucket="test")   # ← Mais intercepté par moto
```

- `moto` simule les APIs AWS **en mémoire** — pas besoin de compte AWS pour les tests
- Le code sous test utilise `boto3` normalement, sans savoir qu'il est mocké
- Si tu mockais manuellement, tu testerais tes mocks, pas ton code
- C'est le standard de l'industrie pour tester du code AWS

---

## 5. `events/` — Pourquoi un dossier dédié aux payloads

```
events/
├── hello_get.json
├── s3_list.json
└── s3_put.json
```

### C'est la convention SAM

```bash
# SAM utilise ces fichiers pour invoquer la Lambda localement
sam local invoke GenAIFunction -e events/hello_get.json

# Ou pour générer un event template
sam local generate-event apigateway aws-proxy > events/custom.json
```

### Pourquoi pas dans `tests/` ?

- Les events servent à **deux choses** : les tests ET le test manuel avec SAM CLI
- Les tests les chargent via la fixture `load_event()` du `conftest.py`
- SAM CLI les utilise directement en ligne de commande
- Les mettre dans `tests/` forcerait SAM à naviguer dans l'arborescence de tests

### Format d'un event (HTTP API v2)

```json
{
    "routeKey": "GET /hello",
    "rawPath": "/hello",
    "queryStringParameters": {
        "name": "Apprenti Pro"
    },
    "requestContext": {
        "http": {
            "method": "GET",
            "path": "/hello"
        },
        "routeKey": "GET /hello"
    }
}
```

Ce format est celui de **HTTP API (v2)**, utilisé par `APIGatewayHttpResolver` de Powertools.
Attention : le format v1 (REST API) utilise `path` et `httpMethod` au lieu de `routeKey` et `rawPath`.
On utilise v2 car HTTP API est plus rapide, moins cher, et suffisant pour la majorité des cas.

---

## 6. Pourquoi pas de dossier `deployment/` ?

On pourrait avoir un `deployment/iam_policy.json` — mais on ne le fait pas. Voici pourquoi :

### Le template SAM est la source de vérité unique

`template.yaml` définit déjà toutes les permissions IAM via `Policies` :

```yaml
Policies:
  - S3CrudPolicy:
      BucketName: !Ref DataBucket
  - Statement:
    - Effect: Allow
      Action: bedrock:InvokeModel
      Resource: "*"
```

Maintenir un fichier IAM séparé crée un **doublon** qui diverge inévitablement du template.
Une seule source de vérité = moins de bugs, moins de confusion.

### Quand un `deployment/` serait justifié

- **Grandes organisations** : l'équipe SecOps impose ses policies via un repo séparé
- **Multi-environnement** : des policies différentes par env (dev/staging/prod)
- **Hors SAM** : si on gère l'IAM avec Terraform ou manuellement

Dans notre cas, SAM gère tout → pas besoin de doublon.

### Least privilege dans le template

**Règle** : on n'accorde que les actions nécessaires, sur les ressources spécifiques.
`S3CrudPolicy` est scopé au bucket spécifique. Bedrock utilise `"*"` car il ne supporte
pas encore le resource-level access control pour `InvokeModel`.

---

## 7. Fichiers racine — Pourquoi chacun existe

### `template.yaml` — Infrastructure as Code (SAM)

```yaml
Transform: AWS::Serverless-2016-10-31  # ← Dit à CloudFormation "c'est du SAM"
```

**Pourquoi SAM plutôt que CloudFormation brut ?**
- SAM est une **surcouche** de CloudFormation spécialisée serverless
- `AWS::Serverless::Function` remplace ~50 lignes de CloudFormation par ~10
- `sam local` permet de tester sans déployer
- C'est l'outil officiel AWS pour Lambda

**Pourquoi pas Terraform ?**
- SAM est natif AWS, zéro setup
- Pour un projet 100% AWS serverless, SAM est plus concis
- Terraform serait pertinent en multi-cloud ou infra complexe

### `samconfig.toml` — Config de déploiement

```toml
[default.deploy.parameters]
stack_name = "genai-prep-week1"
region = "us-east-1"
confirm_changeset = true
```

- Sans ce fichier, `sam deploy` demande les params à chaque fois (`--guided`)
- Avec ce fichier, un `sam deploy` suffit — reproductible et scriptable
- `confirm_changeset = true` : sécurité — SAM montre les changements avant d'appliquer

### `pyproject.toml` — Config Python centralisée

```toml
[tool.pytest.ini_options]
addopts = "-v --tb=short -m 'not integration'"

[tool.ruff]
line-length = 120
```

**Pourquoi un seul fichier de config ?**
- Avant, on avait `setup.cfg`, `pytest.ini`, `.flake8`, `tox.ini`... un par outil
- `pyproject.toml` est le standard PEP 518/621 — **un fichier pour tout**
- pytest, ruff (linter), black (formatter), mypy... tous le supportent

### `requirements.txt` — Dépendances production

```
aws-lambda-powertools>=2.0.0
```

**Pourquoi seulement Powertools ?**
- `boto3` est **déjà inclus** dans le runtime Lambda AWS — l'embarquer ajoute ~50 MB inutiles
- Powertools n'est pas dans le runtime → on l'ajoute (ou on utilise le Lambda Layer officiel)
- Garder ce fichier minimal = packages Lambda plus légers = cold starts plus rapides

### `requirements-dev.txt` — Dépendances dev/tests

```
-r requirements.txt   # Réutilise la production
boto3>=1.34.0         # Nécessaire en local (pas dans le runtime Lambda)
pytest>=8.0.0         # Framework de tests
moto>=5.0.0           # Simulation AWS pour les tests
```

**Pourquoi deux fichiers ?**
- On ne veut pas déployer `pytest` et `moto` dans la Lambda
- `-r requirements.txt` inclut automatiquement les deps de prod → DRY
- `pip install -r requirements-dev.txt` en local donne tout ce qu'il faut

**Pourquoi pas dans `pyproject.toml` ?**
- `requirements.txt` est compris par `pip install -r` directement
- SAM et les CI/CD le supportent nativement
- Pour un projet simple, c'est suffisant. `pyproject.toml` + `pip-tools` c'est pour les gros projets

### `.gitignore` — Hygiène du repo

```gitignore
__pycache__/     # Cache Python — régénéré automatiquement
.pytest_cache/   # Cache pytest
.aws-sam/        # Build SAM — régénéré par sam build
.venv/           # Environnement virtuel — chaque dev a le sien
.env             # Variables d'env — JAMAIS dans git (secrets!)
```

**Règle d'or** : ne versionner que ce qui est nécessaire pour reconstruire le projet.
Tout ce qui est généré ou personnel → `.gitignore`.

---

## 8. Pourquoi `__init__.py` partout

```
src/__init__.py
tests/__init__.py
tests/unit/__init__.py
tests/integration/__init__.py
```

Fichier vide, mais essentiel :

1. **Déclare un package Python** — sans ça, `import lambda_function` ne fonctionne pas depuis les tests
2. **Résout les conflits de noms** — si deux dossiers ont un `conftest.py`, Python doit savoir que ce sont des packages différents
3. **Permet le namespace packaging** — pytest découvre les tests correctement grâce aux `__init__.py`

**Règle** : tout dossier qui contient du `.py` devrait avoir un `__init__.py`.

---

## 9. Choix des outils — Résumé

| Outil | Rôle | Pourquoi celui-là |
|-------|------|------------------|
| **Python 3.12** | Langage | Runtime Lambda le plus récent supporté par AWS |
| **AWS Lambda Powertools** | Routing + Logging | Décorateurs @app.get/@app.post, Logger structuré, standard AWS |
| **boto3** | SDK AWS | La seule façon d'appeler les services AWS depuis Python |
| **pytest** | Tests | Standard Python. Fixtures, markers, plugins, parallélisation |
| **moto** | Mock AWS | Simule les APIs AWS en mémoire. Pas de compte AWS pour tester |
| **SAM** | IaC + local dev | Natif AWS, fait pour serverless. `sam local` pour le dev |
| **ruff** | Linter | 10-100x plus rapide que flake8/pylint. Remplace plusieurs outils |
| **HTTP API (v2)** | HTTP endpoint | Plus rapide et moins cher que REST API (v1). Suffisant pour la majorité |

---

## 10. Patterns à retenir pour tes futurs projets

### Pattern 1 : Utiliser AWS Lambda Powertools (pas de if/elif)

❌ **AVANT (anti-pattern)** :
```python
def lambda_handler(event, context):
    path = event.get("path", "/")
    if path == "/hello":
        return _hello(params)
    elif path == "/s3/list":
        return _s3_list_objects(params)
```

✅ **MAINTENANT (pro, avec Powertools)** :
```python
from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import APIGatewayHttpResolver, Response

logger = Logger()
app = APIGatewayHttpResolver()

@app.get("/hello")
def hello():
    name = app.current_event.get_query_string_value("name", "World")
    return {"message": f"Hello, {name}!"}

@app.post("/s3/put")
def s3_put():
    body = app.current_event.json_body
    # ... logique S3
    return {"message": "Object created"}

@logger.inject_lambda_context
def lambda_handler(event, context):
    return app.resolve(event, context)
```

**Avantages** :
- Décorateurs clairs : une route = une fonction
- `app.current_event` donne accès typé aux query params, body, headers
- Logging structuré avec `@logger.inject_lambda_context`
- Résolution de routes automatique — plus besoin de if/elif
- Les handlers retournent des dicts simples pour les 200, `Response()` pour les erreurs

### Pattern 2 : Séparer requirements.txt (production) et requirements-dev.txt

**Pourquoi ?**
- La Lambda runtime a déjà `boto3` préinstallé — pas besoin de l'embarquer (+50 MB)
- Les tests (pytest, moto) sont pour le dev local, pas pour la production
- Déployer léger = démarrages plus rapides

**requirements.txt** (production, embarqué dans la Lambda) :
```
aws-lambda-powertools>=2.0.0
```

**requirements-dev.txt** (local dev/tests) :
```
-r requirements.txt
boto3>=1.34.0
pytest>=8.0.0
moto>=5.0.0
```

L'option `-r requirements.txt` réutilise la production, puis ajoute les dev tools.

### Pattern 3 : Déplacer les scripts dans un dossier séparé

❌ **Ne fais pas** :
```
src/
├── lambda_function.py
└── s3_operations.py  # ← Script CLI dans src = confus
```

✅ **Fais** :
```
src/
└── lambda_function.py

scripts/
├── s3_operations.py  # ← Scripts/outils de dev
└── README.md
```

Les scripts ne font pas partie de la Lambda déployée. Les séparer physiquement le rend clair.

---

## 11. Checklist — Reproduire cette structure sur un nouveau projet

```bash
mkdir mon-projet && cd mon-projet
mkdir -p src tests/unit tests/integration events scripts
touch src/__init__.py tests/__init__.py tests/unit/__init__.py tests/integration/__init__.py
touch src/lambda_function.py
touch tests/unit/conftest.py tests/unit/test_main.py
touch template.yaml samconfig.toml pyproject.toml requirements.txt requirements-dev.txt .gitignore
```

1. Écrire le handler dans `src/` avec **AWS Lambda Powertools Router** (pas if/elif)
2. Définir l'infra dans `template.yaml`
3. Écrire les tests dans `tests/unit/`
4. Ajouter les events de test dans `events/`
5. Lancer `pytest` → tout doit passer
6. `sam build && sam deploy` → déployer
7. Lancer les tests d'intégration → valider le déploiement

---

## Checklist Production-Ready

- ✅ Handler avec Powertools Router (pas de if/elif)
- ✅ `requirements.txt` vide (ou juste Powertools), `requirements-dev.txt` complet
- ✅ `scripts/` séparé de `src/`
- ✅ Tests unit rapides + integration optionnels
- ✅ `samconfig.toml` pour déploiements reproductibles
- ✅ `pyproject.toml` config centralisée
- ✅ SAM template as source of truth pour les permissions IAM
- ✅ `.gitignore` strict (pas de `__pycache__`, `.env`, etc.)
- ✅ Logging structuré (Powertools Logger)
- ✅ Type hints (APIGatewayProxyEvent, LambdaContext)
