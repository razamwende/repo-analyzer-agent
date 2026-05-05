from pathlib import Path
from datetime import datetime

def save_report(content: str, output_path: str):
    """Sauvegarde le rapport et affiche un résumé."""
    date = datetime.now().strftime("%Y-%m-%d %H:%M")
    dated_content = f"*Rapport généré le {date}*\n\n{content}"
    Path(output_path).write_text(dated_content, encoding="utf-8")
    print(f"\n✅ Rapport sauvegardé : {output_path}")
    # Afficher les 10 premières lignes
    lines = content.split("\n")[:10]
    print("\n" + "\n".join(lines) + "\n...")