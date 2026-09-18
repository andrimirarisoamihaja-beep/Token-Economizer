import json
import os
import subprocess
import sys
from groq import Groq

# -------------------- CONFIGURATION --------------------
TIMEOUT_SECONDES = 60
DOSSIER_SCRIPT = os.path.dirname(os.path.abspath(__file__))
CONFIG_ESLINT_DEFAUT = os.path.join(DOSSIER_SCRIPT, "_default_eslint.config.mjs")

# Contenu d'une config ESLint universelle (ne nécessite aucun package externe)
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


def creer_config_eslint_si_besoin():
    """Crée un fichier de configuration ESLint par défaut si inexistant."""
    if not os.path.exists(CONFIG_ESLINT_DEFAUT):
        with open(CONFIG_ESLINT_DEFAUT, "w", encoding="utf-8") as f:
            f.write(CONTENU_ESLINT_DEFAUT.strip())


# -------------------- FONCTIONS UTILITAIRES --------------------
def executer_commande(commande, timeout=TIMEOUT_SECONDES):
    """Exécute une commande sans bloquer sur l'entrée clavier."""
    try:
        resultat = subprocess.run(
            commande,
            capture_output=True,
            text=True,
            shell=True,
            stdin=subprocess.DEVNULL,
            timeout=timeout,
        )
        return resultat.returncode, resultat.stdout + resultat.stderr
    except subprocess.TimeoutExpired:
        return (
            -1,
            f"TIMEOUT : la commande a dépassé {timeout}s.\nCommande : {commande}\n",
        )
    except Exception as e:
        return -1, f"ERREUR système : {e}\n"


def has_npm_test_script(dossier):
    """Vérifie si un vrai script de test existe."""
    pkg = os.path.join(dossier, "package.json")
    if not os.path.isfile(pkg):
        return False
    try:
        with open(pkg, "r", encoding="utf-8") as f:
            data = json.load(f)
        test_cmd = data.get("scripts", {}).get("test", "")
        # On ignore le script par défaut inutile de npm init
        if "no test specified" in test_cmd or not test_cmd:
            return False
        return True
    except Exception:
        return False


# -------------------- SÉLECTION DE LA CIBLE --------------------
if len(sys.argv) > 1:
    cible = sys.argv[1]
else:
    saisie = input(
        "Entrez le fichier ou dossier a verifier (ex: main.js, app.py) : "
    ).strip()
    cible = saisie if saisie else "main.js"

if not os.path.exists(cible):
    print(f"ERREUR : La cible '{cible}' n'existe pas.")
    sys.exit(1)

# Détection langage
extension = os.path.splitext(cible)[1].lower()
est_typescript = extension in [".ts", ".tsx"]
est_javascript = extension in [".js", ".jsx", ".mjs", ".cjs"] or est_typescript

if os.path.isdir(cible) and os.path.exists(
    os.path.join(cible, "package.json")
):
    est_javascript = True

racine_projet = (
    cible
    if os.path.isdir(cible)
    else os.path.dirname(os.path.abspath(cible)) or "."
)


# -------------------- IA GROQ --------------------
def demander_explication_ia(erreurs: str, langage: str):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print(
            "ATTENTION : Clé GROQ_API_KEY non détectée. Analyse IA désactivée."
        )
        return

    client = Groq(api_key=api_key)
    print(f"\nL'IA analyse le code {langage}...\n")

    prompt = f"""
    Analyse ces erreurs détectées dans du code {langage} et fais une synthèse ultra-claire :

    ```text
    {erreurs}
    ```

    Format STRICT (sans icônes, sans bavardage) :
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
    except Exception as e:
        print(f"Erreur API Groq : {e}")


# -------------------- VÉRIFICATIONS --------------------
erreurs_detectees = ""
langage_nom = ""

if est_javascript:
    langage_nom = "TypeScript" if est_typescript else "JavaScript"
    print(
        f"Vérification {langage_nom} sur : '{cible}' (Qualité, Types, Tests)...\n"
    )

    creer_config_eslint_si_besoin()

    # On vérifie si le projet cible a déjà son propre eslint.config.*
    config_existante = any(
        os.path.exists(os.path.join(racine_projet, f))
        for f in [
            "eslint.config.js",
            "eslint.config.mjs",
            "eslint.config.cjs",
        ]
    )

    # Si pas de config dans le projet cible, on force l'utilisation de notre config par défaut
    option_config = (
        "" if config_existante else f'--config "{CONFIG_ESLINT_DEFAUT}"'
    )

    # 1. ESLint
    code_eslint, sortie_eslint = executer_commande(
        f'npx --yes eslint {option_config} "{cible}"'
    )
    if code_eslint != 0:
        erreurs_detectees += (
            f"--- QUALITE DU CODE (ESLINT) ---\n{sortie_eslint}\n"
        )

    # 2. TypeScript (si applicable)
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
            erreurs_detectees += (
                f"--- TESTS UNITAIRES ---\n{sortie_test}\n"
            )

else:
    langage_nom = "Python"
    print(
        f"Vérification Python sur : '{cible}' (Qualité, Types, Tests)...\n"
    )

    # 1. Ruff
    code_ruff, sortie_ruff = executer_commande(
        f'python -m ruff check "{cible}"'
    )
    if code_ruff != 0:
        erreurs_detectees += (
            f"--- QUALITE DU CODE (RUFF) ---\n{sortie_ruff}\n"
        )

    # 2. Mypy
    code_mypy, sortie_mypy = executer_commande(
        f'python -m mypy "{cible}"'
    )
    if code_mypy != 0:
        erreurs_detectees += (
            f"--- ERREURS DE TYPE (MYPY) ---\n{sortie_mypy}\n"
        )

    # 3. Pytest
    dossier_test = cible if os.path.isdir(cible) else racine_projet
    code_pytest, sortie_pytest = executer_commande(
        f'python -m pytest "{dossier_test}"'
    )
    # On ignore si aucun test n'est trouvé (ce n'est pas une erreur)
    if code_pytest != 0 and "no tests ran" not in sortie_pytest:
        erreurs_detectees += (
            f"--- TESTS UNITAIRES (PYTEST) ---\n{sortie_pytest}\n"
        )

# -------------------- RÉSULTAT FINAL --------------------
if not erreurs_detectees:
    print(f"SUCCES : Le fichier {cible} est propre et sans erreur.")
    sys.exit(0)
else:
    print("PROBLEMES DETECTES :\n")
    print(erreurs_detectees)
    demander_explication_ia(erreurs_detectees, langage_nom)
    sys.exit(1)