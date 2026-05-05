# repo-analyzer-agent

Un agent IA qui clone n'importe quel repository GitHub/GitLab, analyse sa stack technique et sa qualité de code, puis génère un rapport Markdown structuré — en une seule commande.

Construit avec [LangGraph](https://github.com/langchain-ai/langgraph) et Claude (Anthropic).

## Ce que ça fait

1. **Clone** le repository (clone superficiel, depth=1)
2. **Détecte la stack** — langages, frameworks, outils de build
3. **Calcule les métriques qualité** — ratio de tests, présence CI/CD, documentation, hygiène `.gitignore`
4. **Lit les fichiers clés** — README, `pom.xml`, `package.json`, `docker-compose.yml`, etc.
5. **Génère un rapport** en Markdown avec les points forts et des recommandations priorisées

## Prérequis

- Python 3.12+
- Une [clé API Anthropic](https://console.anthropic.com)

## Installation

```bash
git clone https://github.com/your-username/repo-analyzer-agent
cd repo-analyzer-agent

python -m venv .venv
source .venv/bin/activate

pip install -e ".[dev]"
```

Crée un fichier `.env` à la racine du projet :

```bash
ANTHROPIC_API_KEY=sk-ant-...
```

## Utilisation

```bash
python main.py https://github.com/pallets/flask
```

Par défaut, le rapport est sauvegardé dans `rapport.md`. Utilise `--output` pour changer le chemin :

```bash
python main.py https://github.com/pallets/flask --output rapports/flask.md
```

## Exemple de rapport généré

```markdown
## Stack détectée
- Langages : Python
- Frameworks : —
- Outils : pip, github-actions

## Métriques de qualité
| Métrique          | Valeur |
|-------------------|--------|
| Ratio de tests    | 34.2%  |
| CI/CD             | Oui    |
| Documentation     | Oui    |
| .gitignore (.env) | Oui    |

## Points forts
...

## Recommandations
...
```

## Structure du projet

```
repo-analyzer-agent/
├── agent/
│   ├── agent.py      # Définition de l'agent LangGraph
│   ├── tools.py      # Outils LangChain (clone, détection, métriques, lecture)
│   ├── reporter.py   # Sauvegarde du rapport
│   └── main.py       # Point d'entrée CLI (Click)
├── tests/
│   └── test_tools.py
├── main.py
└── pyproject.toml
```

## Lancer les tests

```bash
pytest
```

## Stacks supportées

| Langage                  | Détecté via                        | Frameworks                          |
|--------------------------|------------------------------------|-------------------------------------|
| Python                   | `requirements.txt`, `pyproject.toml` | —                                 |
| Java                     | `pom.xml`, `build.gradle`          | Spring Boot, Quarkus                |
| JavaScript / TypeScript  | `package.json`                     | React, Vue, Angular, Next, Express  |
| Go                       | `go.mod`                           | —                                   |
| Rust                     | `Cargo.toml`                       | —                                   |

La détection CI/CD couvre GitHub Actions, GitLab CI et Jenkinsfile.

## Licence

[MIT](LICENSE)
