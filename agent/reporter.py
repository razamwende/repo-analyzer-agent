from pathlib import Path
from datetime import datetime

def save_report(content: str, output_path: str):
    """Sauvegarde le rapport et affiche un résumé."""
    Path(output_path).write_text(content, encoding="utf-8")
    print(f"\n✅ Rapport sauvegardé : {output_path}")
    # Afficher les 10 premières lignes
    lines = content.split("\n")[:10]
    print("\n" + "\n".join(lines) + "\n...")