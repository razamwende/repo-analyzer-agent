# Guide de contribution

Merci de l'intérêt porté au projet. Ce document explique comment contribuer efficacement.

## Prérequis

- Python 3.12+
- Une clé API Anthropic (pour les tests d'intégration)
- `git`

## Installation de l'environnement de développement

```bash
git clone https://github.com/your-username/repo-analyzer-agent
cd repo-analyzer-agent

python -m venv .venv
source .venv/bin/activate

pip install -e ".[dev]"
pip install ruff
```

Crée un fichier `.env` à la racine :

```
ANTHROPIC_API_KEY=sk-ant-...
```

## Workflow de contribution

1. **Forke** le repository et crée une branche depuis `main`
2. **Nomme ta branche** selon la convention : `feat/ma-fonctionnalite`, `fix/nom-du-bug`, `docs/mise-a-jour`
3. **Développe** en respectant les conventions ci-dessous
4. **Teste** : `pytest` doit passer sans erreur
5. **Lint** : `ruff check .` doit passer sans avertissement
6. **Ouvre une Pull Request** avec une description claire

## Conventions de code

### Style général

- Formatage : **ruff** (ligne max : 100 caractères)
- Typage : toutes les fonctions publiques doivent avoir des annotations de type
- Docstrings : format **Google style**, compatibles MkDocs/Sphinx (voir section dédiée)

### Nommage

| Élément | Convention | Exemple |
|---|---|---|
| Fonctions / variables | `snake_case` | `detect_stack` |
| Classes | `PascalCase` | `ReportGenerator` |
| Constantes | `UPPER_SNAKE_CASE` | `CLONE_DIR` |
| Fichiers | `snake_case` | `tools.py` |

### Docstrings (Google style)

Toutes les fonctions publiques doivent avoir une docstring dans ce format :

```python
def ma_fonction(param: str) -> dict:
    """Résumé en une ligne.

    Description plus longue si nécessaire.

    Args:
        param: Description du paramètre.

    Returns:
        Description de la valeur retournée.

    Raises:
        ValueError: Si le paramètre est invalide.
    """
```

### Outils LangChain (`@tool`)

La docstring de chaque outil LangChain sert de description pour le LLM. Elle doit :
- Être concise et en français
- Préciser le format d'entrée attendu
- Préciser le format de sortie

```python
@tool
def mon_outil(input: str) -> str:
    """Fait X à partir de Y. Retourne un JSON avec les clés A et B."""
```

## Lancer les tests

```bash
# Tous les tests
pytest

# Avec couverture
pytest --cov=agent --cov-report=term-missing

# Un fichier spécifique
pytest tests/test_tools.py -v
```

## Lancer le lint

```bash
ruff check .

# Correction automatique des erreurs simples
ruff check . --fix
```

## Ajouter un nouvel outil

1. Crée la fonction dans `agent/tools.py` avec le décorateur `@tool`
2. Ajoute-la dans la liste `tools` dans `agent/agent.py`
3. Écris au moins un test dans `tests/test_tools.py`
4. Documente le flux dans `docs/architecture.md` si le comportement de l'agent change

## Signaler un bug

Ouvre une issue GitHub en précisant :
- La commande exacte exécutée
- Le message d'erreur complet
- La version de Python (`python --version`)
- Les versions des dépendances (`pip list`)
