import os
from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent
from .tools import clone_repository, detect_stack, compute_quality_metrics, read_key_files

tools = [clone_repository, detect_stack, compute_quality_metrics, read_key_files]

SYSTEM_PROMPT = """
Tu es un expert en architecture logicielle. Tu analyses des repositories de code.
Tu utilises les outils disponibles dans cet ordre :
1. clone_repository : cloner le repo
2. detect_stack : détecter la stack technique
3. compute_quality_metrics : calculer les métriques de qualité
4. read_key_files : lire les fichiers importants

Après avoir utilisé tous les outils, rédige un rapport structuré en Markdown avec :
- Stack détectée
- Métriques de qualité sous forme de tableau
- 3 points forts du projet
- 3 recommandations prioritaires
Sois précis, factuel et actionnable.
"""


def create_agent():
    """Instancie et retourne un agent ReAct LangGraph prêt à l'emploi.

    Initialise un `ChatAnthropic` avec le modèle `claude-sonnet-4-6` et le connecte
    aux quatre outils d'analyse via `create_react_agent`. La clé API est lue depuis
    la variable d'environnement `ANTHROPIC_API_KEY`.

    Returns:
        Un agent LangGraph (`CompiledGraph`) invocable via `.invoke()`.

    Raises:
        KeyError: Si la variable d'environnement `ANTHROPIC_API_KEY` n'est pas définie.
    """
    llm = ChatAnthropic(
        model="claude-sonnet-4-6",
        api_key=os.environ["ANTHROPIC_API_KEY"],
    )
    return create_react_agent(llm, tools, prompt=SYSTEM_PROMPT)


def analyze_repo(url: str) -> str:
    """Analyse un repository distant et retourne un rapport Markdown.

    Crée un agent, l'invoque avec l'URL fournie et retourne le contenu
    du dernier message produit par le LLM (le rapport final).

    Args:
        url: URL HTTPS du repository à analyser (ex: https://github.com/user/repo).

    Returns:
        Rapport d'analyse complet au format Markdown.
    """
    agent = create_agent()
    result = agent.invoke({
        "messages": [("human", f"Analyse ce repository et génère un rapport complet : {url}")]
    })
    return result["messages"][-1].content
