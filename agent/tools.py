import json
import shutil
from pathlib import Path
from langchain.tools import tool
import git

CLONE_DIR = Path("/tmp/repo-analyzer-clones")


@tool
def clone_repository(url: str) -> str:
    """Clone un repository GitHub/GitLab en local et retourne le chemin.

    Effectue un clone superficiel (depth=1) pour limiter la bande passante.
    Si le répertoire de destination existe déjà, il est supprimé avant le clone.

    Args:
        url: URL HTTPS du repository (ex: https://github.com/user/repo).

    Returns:
        Chemin absolu du répertoire cloné sur le système de fichiers local.

    Raises:
        git.exc.GitCommandError: Si l'URL est invalide ou le repository inaccessible.
    """
    repo_name = url.rstrip("/").split("/")[-1].replace(".git", "")
    dest = CLONE_DIR / repo_name
    if dest.exists():
        shutil.rmtree(dest)

    CLONE_DIR.mkdir(parents=True, exist_ok=True)
    git.Repo.clone_from(url, dest, depth=1)
    return str(dest)


@tool
def detect_stack(repo_path: str) -> str:
    """Détecte la stack technique d'un projet à partir de son arborescence.

    Analyse les fichiers de configuration présents pour identifier les langages,
    frameworks et outils utilisés. Inspecte également le contenu de `pom.xml`
    et `package.json` pour affiner la détection des frameworks.

    Args:
        repo_path: Chemin absolu vers le répertoire racine du repository cloné.

    Returns:
        Chaîne JSON avec les clés suivantes :

        - `languages` (list[str]): Langages détectés (ex: ["python", "java"]).
        - `frameworks` (list[str]): Frameworks détectés (ex: ["spring-boot"]).
        - `tools` (list[str]): Outils de build/CI détectés (ex: ["docker", "maven"]).
        - `files_found` (list[str]): Fichiers indicateurs trouvés à la racine.
    """
    root = Path(repo_path)
    stack = {"languages": [], "frameworks": [], "tools": [], "files_found": []}

    INDICATORS = {
        "pom.xml": ("java", "maven"),
        "build.gradle": ("java", "gradle"),
        "package.json": ("javascript/typescript", "node"),
        "requirements.txt": ("python", "pip"),
        "pyproject.toml": ("python", "poetry/setuptools"),
        "go.mod": ("go", "go modules"),
        "Cargo.toml": ("rust", "cargo"),
        "Dockerfile": (None, "docker"),
        ".gitlab-ci.yml": (None, "gitlab-ci"),
        ".github/workflows": (None, "github-actions"),
        "docker-compose.yml": (None, "docker-compose"),
    }

    for filename, (lang, tool_name) in INDICATORS.items():
        path = root / filename
        if path.exists():
            stack["files_found"].append(filename)
            if lang and lang not in stack["languages"]:
                stack["languages"].append(lang)
            if tool_name and tool_name not in stack["tools"]:
                stack["tools"].append(tool_name)

    pom = root / "pom.xml"
    if pom.exists():
        content = pom.read_text(errors="ignore")
        if "spring-boot" in content.lower() or "springframework" in content.lower():
            stack["frameworks"].append("spring-boot")
        if "quarkus" in content.lower():
            stack["frameworks"].append("quarkus")

    pkg = root / "package.json"
    if pkg.exists():
        try:
            data = json.loads(pkg.read_text())
            deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
            for fw in ["react", "angular", "vue", "next", "express"]:
                if any(fw in k.lower() for k in deps):
                    stack["frameworks"].append(fw)
        except Exception:
            pass

    return json.dumps(stack, indent=2, ensure_ascii=False)


@tool
def compute_quality_metrics(repo_path: str) -> str:
    """Calcule les métriques de qualité d'un projet.

    Parcourt récursivement le repository pour compter les fichiers source et de test,
    et vérifie la présence d'indicateurs qualité (CI/CD, documentation, sécurité).

    Args:
        repo_path: Chemin absolu vers le répertoire racine du repository cloné.

    Returns:
        Chaîne JSON avec les clés suivantes :

        - `test_ratio` (float): Pourcentage de fichiers de test par rapport au total.
        - `source_files` (int): Nombre de fichiers source détectés.
        - `test_files` (int): Nombre de fichiers de test détectés.
        - `has_ci` (bool): Présence d'une configuration CI/CD.
        - `has_readme` (bool): Présence d'un fichier README.
        - `has_docs` (bool): Présence d'un dossier `docs/`.
        - `gitignore_covers_env` (bool): Le `.gitignore` protège-t-il les fichiers `.env`.
        - `no_gitignore` (bool): Présent uniquement si aucun `.gitignore` n'est trouvé.
    """
    root = Path(repo_path)
    metrics = {}

    source_files, test_files = [], []

    for file in root.rglob("*.*"):
        if file.is_file():
            if any(ex in file.parts for ex in [".git", "node_modules", "target", "__pycache__"]):
                continue
            if file.suffix in [".py", ".java", ".ts", ".js", ".go"]:
                name_lower = file.name.lower()
                if "test" in name_lower or "spec" in name_lower:
                    test_files.append(str(file))
                else:
                    source_files.append(str(file))

    total = len(source_files) + len(test_files)
    metrics["test_ratio"] = round(len(test_files) / total * 100, 1) if total > 0 else 0
    metrics["source_files"] = len(source_files)
    metrics["test_files"] = len(test_files)

    metrics["has_ci"] = any([
        (root / ".gitlab-ci.yml").exists(),
        (root / ".github" / "workflows").exists(),
        (root / "Jenkinsfile").exists(),
    ])

    metrics["has_readme"] = (root / "README.md").exists() or (root / "README.rst").exists()
    metrics["has_docs"] = (root / "docs").is_dir()

    gitignore = root / ".gitignore"
    if gitignore.exists():
        content = gitignore.read_text()
        metrics["gitignore_covers_env"] = ".env" in content
    else:
        metrics["gitignore_covers_env"] = False
        metrics["no_gitignore"] = True

    return json.dumps(metrics, indent=2, ensure_ascii=False)


@tool
def read_key_files(repo_path: str) -> str:
    """Lit le contenu des fichiers clés pour comprendre le contexte du projet.

    Extrait un aperçu des fichiers de configuration et de documentation principaux.
    Chaque fichier est tronqué à 3000 caractères pour limiter la taille du contexte.

    Args:
        repo_path: Chemin absolu vers le répertoire racine du repository cloné.

    Returns:
        Contenu concaténé des fichiers trouvés, séparés par des en-têtes `=== nom ===`.
        Retourne `"Aucun fichier clé trouvé."` si aucun fichier connu n'est présent.
    """
    root = Path(repo_path)
    content_parts = []
    MAX_CHARS = 3000

    key_files = [
        "README.md", "README.rst", "pom.xml",
        "build.gradle", "package.json", "docker-compose.yml",
    ]

    for filename in key_files:
        path = root / filename
        if path.exists():
            text = path.read_text(errors="ignore")[:MAX_CHARS]
            content_parts.append(f"=== {filename} ===\n{text}")

    return "\n\n".join(content_parts) if content_parts else "Aucun fichier clé trouvé."
