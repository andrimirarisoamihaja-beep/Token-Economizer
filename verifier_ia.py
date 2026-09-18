import io
import json
import os
import subprocess
import sys

from dotenv import load_dotenv
from groq import Groq

# -------------------- FIX ENCODAGE WINDOWS (UTF-8) --------------------
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

load_dotenv()

# -------------------- CONFIGURATION --------------------
TIMEOUT_SECONDES = 60
DOSSIER_SCRIPT = os.path.dirname(os.path.abspath(__file__))
CONFIG_ESLINT_DEFAUT = os.path.join(DOSSIER_SCRIPT, "_default_eslint.config.mjs")

CONTENU_ESLINT_DEFAUT = """
export default [
    {
        languageOptions: {
            ecmaVersion: "latest",
            sourceType: "module",
        },
        rules: {
            "no-unused-vars": "warn",
            "no-undef": "warn",
            "no-unreachable": "error",
            "no-constant-condition": "warn",
            "constructor-super": "error",
            "no-this-before-super": "error"
        }
    }
];
"""


def creer_config_eslint_si_besoin() -> None:
    """Crée un fichier de configuration ESLint par défaut si inexistant."""
    if not os.path.exists(CONFIG_ESLINT_DEFAUT):
        with open(CONFIG_ESLINT_DEFAUT, "w", encoding="utf-8") as f:
            f.write(CONTENU_ESLINT_DEFAUT.strip())


def executer_commande(commande: str, timeout: int = TIMEOUT_SECONDES) -> tuple[int, str]:
    """Exécute une commande sans bloquer sur l'entrée clavier."""
    try:
        resultat = subprocess.run(
            commande,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=True,
            check=False,
            stdin=subprocess.DEVNULL,
            timeout=timeout,
        )
        return resultat.returncode, resultat.stdout + resultat.stderr
    except subprocess.TimeoutExpired:
        return (
            -1,
            f"TIMEOUT : la commande a dépassé {timeout}s.\nCommande : {commande}\n",
        )
    except Exception as e:  # noqa: BLE001
        return -1, f"ERREUR système : {e}\n"


def has_npm_test_script(dossier: str) -> bool:
    """Vérifie si un vrai script de test existe dans package.json."""
    pkg = os.path.join(dossier, "package.json")
    if not os.path.isfile(pkg):
        return False
    try:
        with open(pkg, "r", encoding="utf-8") as f:
            data = json.load(f)
        test_cmd = data.get("scripts", {}).get("test", "")
        return bool(test_cmd) and "no test specified" not in test_cmd
    except Exception:  # noqa: BLE001
        return False


def commande_disponible(nom: str) -> bool:
    """Vérifie si une commande existe dans le PATH."""
    code, _ = executer_commande(f"{nom} -version")
    if code == 0:
        return True
    # javac / java renvoient parfois un code non nul mais existent quand même
    code2, sortie2 = executer_commande(f"where {nom}" if sys.platform == "win32" else f"which {nom}")
    return code2 == 0 and bool(sortie2.strip())


def collecter_fichiers_java(cible: str) -> list[str]:
    """Retourne la liste des fichiers .java à analyser."""
    if os.path.isfile(cible) and cible.lower().endswith(".java"):
        return [os.path.abspath(cible)]

    fichiers: list[str] = []
    if os.path.isdir(cible):
        for root, dirs, files in os.walk(cible):
            # Ignorer dossiers inutiles
            dirs[:] = [
                d
                for d in dirs
                if d
                not in {
                    ".git",
                    "node_modules",
                    ".venv",
                    "target",
                    "build",
                    "out",
                    "__pycache__",
                }
            ]
            for name in files:
                if name.lower().endswith(".java"):
                    fichiers.append(os.path.join(root, name))
    return fichiers

def analyser_java(cible: str) -> str:
    """Analyse Java : Compilation via Maven/Gradle si présent, sinon javac."""
    erreurs = ""
    racine = (
        cible
        if os.path.isdir(cible)
        else os.path.dirname(os.path.abspath(cible)) or "."
    )

    # Chercher la racine du projet s'il y a un pom.xml au-dessus
    dossier_parent = racine
    for _ in range(5):  # Remonte jusqu'à 5 dossiers au-dessus
        if os.path.isfile(os.path.join(dossier_parent, "pom.xml")) or os.path.isfile(
            os.path.join(dossier_parent, "build.gradle")
        ):
            racine = dossier_parent
            break
        parent = os.path.dirname(dossier_parent)
        if parent == dossier_parent:
            break
        dossier_parent = parent

    pom = os.path.join(racine, "pom.xml")
    gradle = os.path.join(racine, "build.gradle")
    gradle_kts = os.path.join(racine, "build.gradle.kts")

    # 1. Si projet MAVEN : on compile avec Maven (charge toutes les dépendances .jar)
    if os.path.isfile(pom) and commande_disponible("mvn"):
        print("Projet Maven détecté. Compilation avec Maven...")
        code_mvn, sortie_mvn = executer_commande(
            f'mvn -f "{pom}" test-compile -q',
            timeout=max(TIMEOUT_SECONDES, 180),
        )
        if code_mvn != 0:
            erreurs += f"--- ERREURS DE COMPILATION (MAVEN) ---\n{sortie_mvn}\n"
        return erreurs

    # 2. Si projet GRADLE : on compile avec Gradle
    if (os.path.isfile(gradle) or os.path.isfile(gradle_kts)):
        print("Projet Gradle détecté. Compilation avec Gradle...")
        gradlew = os.path.join(
            racine, "gradlew.bat" if sys.platform == "win32" else "gradlew"
        )
        cmd = f'"{gradlew}" -p "{racine}" testClasses -q' if os.path.isfile(gradlew) else f'gradle -p "{racine}" testClasses -q'
        code_gr, sortie_gr = executer_commande(cmd, timeout=max(TIMEOUT_SECONDES, 180))
        if code_gr != 0:
            erreurs += f"--- ERREURS DE COMPILATION (GRADLE) ---\n{sortie_gr}\n"
        return erreurs

    # 3. Mode secours : Compilation directe avec javac (pour fichiers isolés sans Maven/Gradle)
    fichiers = collecter_fichiers_java(cible)
    if not fichiers:
        return "--- JAVA ---\nAucun fichier .java trouvé.\n"

    if not commande_disponible("javac"):
        return "--- JAVA ---\nERREUR : 'javac' introuvable dans le PATH.\n"

    liste_fichiers = " ".join(f'"{f}"' for f in fichiers)
    out_dir = os.path.join(racine, ".verifier_java_out")
    
    code_javac, sortie_javac = executer_commande(
        f'javac -Xlint:all -encoding UTF-8 -d "{out_dir}" {liste_fichiers}'
    )

    if code_javac != 0:
        erreurs += f"--- COMPILATION JAVA (JAVAC) ---\n{sortie_javac}\n"

    return erreurs

def demander_explication_ia(erreurs: str, langage: str) -> None:
    """Consulte l'IA Groq pour expliquer et corriger les erreurs."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("ATTENTION : Clé GROQ_API_KEY non détectée. Analyse IA désactivée.")
        return

    client = Groq(api_key=api_key)
    print(f"\nL'IA analyse le code {langage}...\n")

    prompt = f"""
    Analyse ces erreurs détectées dans du code {langage} et fais une synthèse ultra-claire :

    ```text
    {erreurs}
    ```

    Format STRICT (sans icônes) :
    Emplacement : [Fichier] -> [Ligne/Fonction]
    Probleme : [Description courte du bogue]
    Correction : [Code ou solution exacte]
    """

    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="openai/gpt-oss-120b",
            temperature=0.1,
        )
        print("--- SYNTHESE IA ---")
        print(chat_completion.choices[0].message.content)
    except Exception as e:  # noqa: BLE001
        print(f"Erreur API Groq : {e}")


def main() -> None:
    # -------------------- SÉLECTION DE LA CIBLE --------------------
    if len(sys.argv) > 1:
        cible = sys.argv[1]
    else:
        saisie = input(
            "Entrez le fichier ou dossier a verifier (ex: main.js, app.py, Main.java) : "
        ).strip()
        cible = saisie if saisie else "main.js"

    if not os.path.exists(cible):
        print(f"ERREUR : La cible '{cible}' n'existe pas.")
        sys.exit(1)

    # Détection du langage
    extension = os.path.splitext(cible)[1].lower()
    est_java = extension == ".java"
    est_typescript = extension in [".ts", ".tsx"]
    est_javascript = extension in [".js", ".jsx", ".mjs", ".cjs"] or est_typescript

    if os.path.isdir(cible):
        # Un dossier peut être multi-langage : on priorise selon le contenu
        contient_java = any(
            f.lower().endswith(".java") for f in collecter_fichiers_java(cible)
        )
        if os.path.exists(os.path.join(cible, "package.json")):
            est_javascript = True
            est_java = False
        elif (
            os.path.exists(os.path.join(cible, "pom.xml"))
            or os.path.exists(os.path.join(cible, "build.gradle"))
            or os.path.exists(os.path.join(cible, "build.gradle.kts"))
            or contient_java
        ):
            est_java = True
            est_javascript = False

    # Fichier unique .java
    if extension == ".java":
        est_java = True
        est_javascript = False

    racine_projet = (
        cible if os.path.isdir(cible) else os.path.dirname(os.path.abspath(cible)) or "."
    )

    erreurs_detectees = ""
    langage_nom = ""

    # -------------------- VÉRIFICATIONS --------------------
    if est_java:
        langage_nom = "Java"
        print(f"Vérification Java sur : '{cible}' (Compilation, Tests)...\n")
        erreurs_detectees += analyser_java(cible)

    elif est_javascript:
        langage_nom = "TypeScript" if est_typescript else "JavaScript"
        print(f"Vérification {langage_nom} sur : '{cible}' (Qualité, Types, Tests)...\n")

        creer_config_eslint_si_besoin()

        config_existante = any(
            os.path.exists(os.path.join(racine_projet, f))
            for f in ["eslint.config.js", "eslint.config.mjs", "eslint.config.cjs"]
        )

        option_config = "" if config_existante else f'--config "{CONFIG_ESLINT_DEFAUT}"'

        # 1. ESLint
        code_eslint, sortie_eslint = executer_commande(
            f'npx --yes eslint {option_config} "{cible}"'
        )
        if code_eslint != 0:
            erreurs_detectees += f"--- QUALITE DU CODE (ESLINT) ---\n{sortie_eslint}\n"

        # 2. TypeScript
        if est_typescript:
            code_tsc, sortie_tsc = executer_commande(
                f'npx --yes tsc "{cible}" --noEmit --allowJs'
            )
            if code_tsc != 0:
                erreurs_detectees += (
                    f"--- ERREURS DE TYPE (TYPESCRIPT) ---\n{sortie_tsc}\n"
                )

        # 3. Tests
        if has_npm_test_script(racine_projet):
            code_test, sortie_test = executer_commande(
                f'npm test --prefix "{racine_projet}" -- --silent --watchAll=false'
            )
            if code_test != 0:
                erreurs_detectees += f"--- TESTS UNITAIRES ---\n{sortie_test}\n"

    else:
        langage_nom = "Python"
        print(f"Vérification Python sur : '{cible}' (Qualité, Types, Tests)...\n")

        # 1. Ruff
        code_ruff, sortie_ruff = executer_commande(f'python -m ruff check "{cible}"')
        if code_ruff != 0:
            erreurs_detectees += f"--- QUALITE DU CODE (RUFF) ---\n{sortie_ruff}\n"

        # 2. Mypy
        code_mypy, sortie_mypy = executer_commande(f'python -m mypy "{cible}"')
        if code_mypy != 0:
            erreurs_detectees += f"--- ERREURS DE TYPE (MYPY) ---\n{sortie_mypy}\n"

        # 3. Pytest
        dossier_test = cible if os.path.isdir(cible) else racine_projet
        code_pytest, sortie_pytest = executer_commande(
            f'python -m pytest "{dossier_test}"'
        )
        if code_pytest != 0 and "no tests ran" not in sortie_pytest:
            erreurs_detectees += f"--- TESTS UNITAIRES (PYTEST) ---\n{sortie_pytest}\n"

    # -------------------- RÉSULTAT FINAL --------------------
    if not erreurs_detectees:
        print(f"SUCCES : Le fichier {cible} est propre et sans erreur.")
        sys.exit(0)

    print("PROBLEMES DETECTES :\n")
    print(erreurs_detectees)
    demander_explication_ia(erreurs_detectees, langage_nom)
    sys.exit(1)


if __name__ == "__main__":
    main()