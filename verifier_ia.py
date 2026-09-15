import os
import subprocess
import sys
from groq import Groq


def demander_explication_ia(erreurs: str):
    """Envoie l'erreur à Groq et affiche l'emplacement et la correction sans icônes."""
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        print(
            "ATTENTION : Cle GROQ_API_KEY non detectee. L'analyse IA est desactivee."
        )
        return

    client = Groq(api_key=api_key)

    print("\nL'IA (Groq) analyse la qualite et les erreurs du code...\n")

    prompt = f"""
    Analyse ces problemes de code Python (Mauvaises pratiques, Mypy ou Pytest) et fais une synthese ULTRA COURTE.

    ```text
    {erreurs}
    ```

    Respecte STRICTEMENT ce format (sans introduction, sans conclusion, et SANS AUCUNE ICONE NI EMOJI) :
    Emplacement : [Nom du fichier] -> [Numéro de ligne ou Nom de la fonction]
    Probleme : [1 phrase sur le bogue ou la mauvaise pratique]
    Correction : [La modification exacte a effectuer]
    """

    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="openai/gpt-oss-120b",
            temperature=0.1,
        )

        print("SYNTHESE IA :")
        print("--------------------------------------------------")
        print(chat_completion.choices[0].message.content)
        print("--------------------------------------------------")

    except Exception as e:
        print(f"Erreur lors de l'appel a l'API Groq : {e}")


def executer_commande(commande):
    resultat = subprocess.run(
        commande, capture_output=True, text=True, shell=True
    )
    return resultat.returncode, resultat.stdout + resultat.stderr


# --- DEBUTER LA VERIFICATION ---
print("Verification globale du code (Qualite, Types, Tests)...\n")
erreurs_detectees = ""

# 1. Verification des MAUVAISES PRATIQUES et de la STRUCTURE (Ruff)
code_ruff, sortie_ruff = executer_commande("python -m ruff check calcul.py")
if code_ruff != 0:
    erreurs_detectees += (
        f"--- MAUVAISES PRATIQUES / STRUCTURE (RUFF) ---\n{sortie_ruff}\n"
    )

# 2. Verification du TYPAGE (Mypy)
code_mypy, sortie_mypy = executer_commande("python -m mypy calcul.py")
if code_mypy != 0:
    erreurs_detectees += f"--- ERREURS DE TYPE (MYPY) ---\n{sortie_mypy}\n"

# 3. Verification des TESTS UNITAIRES (Pytest)
code_pytest, sortie_pytest = executer_commande("python -m pytest")
if code_pytest != 0:
    erreurs_detectees += f"--- ECHEC DES TESTS (PYTEST) ---\n{sortie_pytest}\n"

# --- TRAITEMENT DES RESULTATS ---
if not erreurs_detectees:
    print(
        "SUCCES : Le code respecte les bonnes pratiques et passe tous les tests."
    )
    sys.exit(0)
else:
    print("ERREUR : Des problemes ont ete detectes !")
    print(erreurs_detectees)

    # Appel de l'IA Groq
    demander_explication_ia(erreurs_detectees)
    sys.exit(1)