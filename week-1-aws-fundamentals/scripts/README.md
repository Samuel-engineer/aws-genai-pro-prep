# Scripts — Utilitaires et exercices

Ce dossier contient des **scripts utilitaires** — des outils de développement et des exercices,
pas du code qui fait partie de la Lambda.

## `s3_operations.py`

Exercice standalone pour pratiquer boto3 et les opérations S3.

### Usage

```bash
# Depuis la racine du projet
cd scripts/
python s3_operations.py --bucket BUCKET_NAME --action list

python s3_operations.py --bucket BUCKET_NAME --action upload --key data/test.txt --file ../README.md

python s3_operations.py --bucket BUCKET_NAME --action download --key data/test.txt --file ./output.txt

python s3_operations.py --bucket BUCKET_NAME --action create-bucket --region us-east-1

python s3_operations.py --bucket BUCKET_NAME --action info
```

### Pourquoi ici et pas dans `src/` ?

- Les scripts ne font pas partie de la Lambda déployée
- Les scripts sont testés manuellement, pas automatiquement par pytest
- Les scripts peuvent invoquer la Lambda, l'instruire, la tester — ce sont des outils de développement
