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
    llm = ChatAnthropic(
        model="claude-sonnet-4-6",
        api_key=os.environ["ANTHROPIC_API_KEY"],
    )
    return create_react_agent(llm, tools, prompt=SYSTEM_PROMPT)


def analyze_repo(url: str) -> str:
    agent = create_agent()
    result = agent.invoke({
        "messages": [("human", f"Analyse ce repository et génère un rapport complet : {url}")]
    })
    return result["messages"][-1].content
