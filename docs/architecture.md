# Architecture

## Vue d'ensemble

`repo-analyzer-agent` est un agent ReAct construit avec LangGraph. Il reçoit une URL de repository, orchestre une séquence d'outils, puis produit un rapport Markdown.

```
Entrée utilisateur (URL)
        │
        ▼
┌───────────────────┐
│   create_agent()  │  ← ChatAnthropic (claude-sonnet-4-6)
│   LangGraph       │
│   ReAct Agent     │
└────────┬──────────┘
         │ invoke()
         ▼
┌─────────────────────────────────────────┐
│              Boucle ReAct               │
│                                         │
│  ┌─────────────────────────────────┐    │
│  │  1. clone_repository(url)       │    │
│  │     → /tmp/repo-analyzer-clones │    │
│  └──────────────┬──────────────────┘    │
│                 ▼                       │
│  ┌─────────────────────────────────┐    │
│  │  2. detect_stack(repo_path)     │    │
│  │     → JSON stack                │    │
│  └──────────────┬──────────────────┘    │
│                 ▼                       │
│  ┌─────────────────────────────────┐    │
│  │  3. compute_quality_metrics()   │    │
│  │     → JSON métriques            │    │
│  └──────────────┬──────────────────┘    │
│                 ▼                       │
│  ┌─────────────────────────────────┐    │
│  │  4. read_key_files(repo_path)   │    │
│  │     → contenu des fichiers clés │    │
│  └──────────────┬──────────────────┘    │
│                 ▼                       │
│        Synthèse par le LLM              │
└─────────────────┬───────────────────────┘
                  ▼
         Rapport Markdown
                  │
                  ▼
         save_report() → rapport.md
```

## Graphe LangGraph

L'agent utilise `langgraph.prebuilt.create_react_agent`, qui génère un graphe avec deux nœuds :

```
START
  │
  ▼
┌──────────┐     appel outil      ┌──────────────┐
│  agent   │ ──────────────────►  │  tools node  │
│  (LLM)   │ ◄──────────────────  │              │
└──────────┘    résultat outil    └──────────────┘
  │
  │  (aucun appel outil → réponse finale)
  ▼
 END
```

Le LLM décide à chaque itération s'il appelle un outil ou s'il termine. LangGraph gère l'état (`messages`) et le routage automatiquement.

## Flux de données

| Étape | Entrée | Sortie |
|---|---|---|
| `clone_repository` | URL HTTPS | Chemin local (`str`) |
| `detect_stack` | Chemin local | JSON `{languages, frameworks, tools, files_found}` |
| `compute_quality_metrics` | Chemin local | JSON `{test_ratio, has_ci, has_readme, ...}` |
| `read_key_files` | Chemin local | Contenu brut des fichiers clés (tronqué à 3000 chars/fichier) |
| Synthèse LLM | Tous les résultats d'outils | Rapport Markdown structuré |

## Modules

```
agent/
├── agent.py     # Instanciation du LLM, création et invocation de l'agent
├── tools.py     # Outils LangChain (@tool) utilisés par l'agent
├── reporter.py  # Écriture du rapport sur disque
└── main.py      # CLI Click (point d'entrée)
```

## Dépendances clés

| Package | Rôle |
|---|---|
| `langchain-anthropic` | Intégration Claude via LangChain |
| `langgraph` | Orchestration de l'agent ReAct |
| `langchain-core` | Abstractions communes (outils, messages) |
| `gitpython` | Clone de repository via `git` |
| `click` | Interface en ligne de commande |
| `python-dotenv` | Chargement de la clé API depuis `.env` |
