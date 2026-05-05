import os
import json
import shutil
from pathlib import Path
from langchain.tools import tool
import git

CLONE_DIR = Path("/tmp/repo-analyzer-clones")

@tool
def clone_repository(url: str) -> str:
    """
    Clone un repository GitHub/GitLab et retourne le chemin local.
    Accepte une URL HTTPS (ex: https://github.com/user/repo).
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
    """
    Détecte la stack technique d'un projet : langages, frameworks, outils.
    Retourne un JSON avec la stack détectée.
    """
    root = Path(repo_path)
    stack = {"languages": [], "frameworks": [], "tools": [], "files_found": []}

    # Détection par fichiers de configuration
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
    
    # Détection de frameworks via contenu
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
    """
    Calcule les métriques de qualité du projet :
    ratio de tests, présence CI/CD, documentation, secrets exposés.
    """
    root = Path(repo_path)
    metrics = {}

    # Compter fichiers source vs fichiers test
    source_files, test_files =[], []

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
    metrics["test_ratio"] = round(len(test_files) / total *100 , 1)if total > 0 else 0
    metrics["source_files"] = len(source_files)
    metrics["test_files"] = len(test_files)

    # Présence CI/CD
    metrics["has_ci"] = any([
        (root / ".gitlab-ci.yml").exists(),
        (root / ".github" / "workflows").exists(),
        (root / "Jenkinsfile").exists(),
    ])
    
    # Documentation
    metrics["has_readme"] = (root / "README.md").exists() or (root / "README.rst").exists()
    metrics["has_docs"] = (root / "docs").is_dir() 

    # Sécurité basique : secrets potentiels dans .env ou fichiers non ignorés
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
   """
   Lit les fichiers clés du projet pour comprendre son contexte :
   README, fichiers de config principaux.
   """
   root = Path(repo_path)
   content_parts = []
   MAX_CHARS = 3000
   
   key_files = ["README.md", "README.rst", "pom.xml", "build.gradle", "package.json", "docker-compose.yml"]
   
   for filename in key_files:
       path = root / filename
       if path.exists():
           text = path.read_text(errors="ignore")[:MAX_CHARS]
           content_parts.append(f"=== {filename} ===\n{text}")

   return "\n\n".join(content_parts) if content_parts else "Aucun fichier clé trouvé."