# AWS Generative AI Professional — Préparation à la certification

Parcours structuré en **8 semaines** pour maîtriser les services AWS liés à l'IA générative et préparer la certification **AWS Certified Machine Learning — Specialty** / **Generative AI Professional**.

Chaque semaine construit sur la précédente. On part des fondamentaux AWS jusqu'à l'optimisation avancée et la préparation à l'examen.

---

## Progression

```
Semaine 1    Semaine 2    Semaine 3    Semaine 4    Semaine 5    Semaine 6    Semaine 7    Semaine 8
   │            │            │            │            │            │            │            │
   ▼            ▼            ▼            ▼            ▼            ▼            ▼            ▼
┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐
│  AWS   │  │Bedrock │  │  RAG   │  │ Agents │  │Sage-   │  │Sécurité│  │Optimi- │  │ Exam   │
│ Fonda- │─▶│ Basics │─▶│Archi-  │─▶│  &     │─▶│Maker   │─▶│  &     │─▶│sations │─▶│ Prep   │
│mentaux │  │        │  │tecture │  │ Tools  │  │JumpSt. │  │  Ops   │  │Avancées│  │        │
└────────┘  └────────┘  └────────┘  └────────┘  └────────┘  └────────┘  └────────┘  └────────┘
 Lambda       Modèles     Embeddings   Function    Fine-       IAM adv.    Latence     Questions
 API GW       Prompts     Vector DB    calling     tuning      Logging     Coûts       Stratégies
 S3           Inférence   Chunking     Orchestr.   Endpoints   Guardrails  Caching     Révision
 IAM/SAM      Streaming   Retrieval    Chaînes     Déploiem.   Monitoring  Évaluation  Simulation
```

---

## Contenu par semaine

### [Week 1 — AWS Fundamentals](week-1-aws-fundamentals/) ✅

> Poser les bases : Lambda, API Gateway, S3, IAM, SAM.

Les building blocks de toute architecture GenAI sur AWS. On construit un projet serverless complet (pas un hello-world jetable) avec tests unitaires, intégration, et déploiement IaC.

**Services** : Lambda · API Gateway · S3 · IAM · SAM  
**Livrables** : API REST déployée, opérations S3, tests unitaires + intégration

---

### [Week 2 — Bedrock Basics](week-2-bedrock-basics/) 🔜

> Appeler les modèles de fondation via Amazon Bedrock.

Première interaction avec les LLMs. Comprendre les APIs d'inférence, le prompt engineering, le streaming de réponses, et la comparaison des modèles disponibles (Claude, Titan, Llama).

**Services** : Amazon Bedrock · Bedrock Runtime  
**Concepts** : Inférence, prompts, température, tokens, streaming

---

### [Week 3 — RAG Architecture](week-3-rag-architecture/) 🔜

> Construire un pipeline Retrieval-Augmented Generation.

On connecte les documents S3 (week 1) aux modèles Bedrock (week 2) via un pipeline RAG complet : ingestion, chunking, embeddings, stockage vectoriel, et retrieval.

**Services** : Bedrock Knowledge Bases · OpenSearch Serverless · S3  
**Concepts** : Embeddings, vector stores, chunking, retrieval, contexte augmenté

---

### [Week 4 — Agents & Tools](week-4-agents-and-tools/) 🔜

> Donner aux LLMs la capacité d'agir : agents et function calling.

Les modèles ne font plus que répondre — ils exécutent des actions. On construit des agents Bedrock avec des action groups, du function calling, et des chaînes d'orchestration.

**Services** : Bedrock Agents · Lambda (action groups) · Step Functions  
**Concepts** : Function calling, orchestration, planning, tool use

---

### [Week 5 — SageMaker JumpStart](week-5-sagemaker-jumpstart/) 🔜

> Déployer et fine-tuner des modèles avec SageMaker.

Quand Bedrock ne suffit pas : déploiement de modèles custom, fine-tuning sur données propriétaires, et gestion d'endpoints d'inférence.

**Services** : SageMaker JumpStart · SageMaker Endpoints · S3  
**Concepts** : Fine-tuning, endpoints, modèles custom, inférence dédiée

---

### [Week 6 — Security & Ops](week-6-security-and-ops/) 🔜

> Sécuriser et opérer les applications GenAI en production.

IAM avancé, guardrails Bedrock, logging, monitoring, et bonnes pratiques opérationnelles pour des workloads GenAI en production.

**Services** : IAM · CloudWatch · Bedrock Guardrails · CloudTrail  
**Concepts** : Least privilege, content filtering, observabilité, audit

---

### [Week 7 — Advanced Optimizations](week-7-advanced-optimizations/) 🔜

> Optimiser les performances, les coûts, et la qualité.

Réduire la latence, optimiser les coûts d'inférence, mettre en cache les réponses, et évaluer la qualité des sorties des modèles.

**Services** : Bedrock · CloudWatch · Lambda · ElastiCache  
**Concepts** : Latence, caching, évaluation, prompt optimization, coûts

---

### [Week 8 — Exam Prep](week-8-exam-prep/) 🔜

> Révision ciblée et simulation d'examen.

Consolidation de tous les concepts, questions de pratique par domaine, stratégies d'examen, et identification des points faibles.

**Livrables** : Fiches de révision, quiz par domaine, examen blanc

---

## Prérequis

- Python 3.12+
- AWS CLI configuré (`aws configure`)
- AWS SAM CLI
- Compte AWS avec accès à Amazon Bedrock
- Git

## Structure du repo

```
aws-genai-pro-prep/
├── week-1-aws-fundamentals/    # ✅ Complété
├── week-2-bedrock-basics/      # 🔜 À venir
├── week-3-rag-architecture/    # 🔜 À venir
├── week-4-agents-and-tools/    # 🔜 À venir
├── week-5-sagemaker-jumpstart/ # 🔜 À venir
├── week-6-security-and-ops/    # 🔜 À venir
├── week-7-advanced-optimizations/ # 🔜 À venir
├── week-8-exam-prep/           # 🔜 À venir
└── README.md
```

## Philosophie

- **Hands-on first** — chaque semaine produit du code déployable, pas juste de la théorie
- **Production-grade** — tests, IaC, bonnes pratiques dès le jour 1
- **Progression cumulative** — chaque semaine réutilise les acquis des précédentes
- **Exam-oriented** — les concepts couverts sont alignés avec les domaines de la certification