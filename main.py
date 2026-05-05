import click
from dotenv import load_dotenv
from agent.agent import analyze_repo
from agent.reporter import save_report

load_dotenv()

@click.command()
@click.argument("url")
@click.option("--output", "-o", default="rapport.md", help="Chemin de sortie du rapport")
def main(url: str, output: str):
    """Analyse un repository et génère un rapport."""
    print(f"\n🔍 Analyse du repository : {url}")
    report = analyze_repo(url)
    save_report(report, output)

if __name__ == "__main__":
    main()