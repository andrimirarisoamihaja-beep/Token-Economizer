import os
import subprocess
import sys
from groq import Groq


def demander_explication_ia(erreurs: str):
    """Envoie l'erreur à Groq et affiche l'emplacement exact et la solution."""
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        print(
            "⚠️ Clé GROQ_API_KEY non détectée. L'analyse IA est désactivée."
        )
        return

    client = Groq(api_key=api_key)

    print("\n⚡ L'IA (Groq) génère la localisation et la solution...\n")

    # Prompt exigeant l'emplacement exact
    prompt = f"""
    Analyse ces erreurs Python (Mypy/Pytest) et fais une synthèse ULTRA COURTE et directe.

    ```text
    {erreurs}
    ```

    Respecte STRICTEMENT ce format (exactement 3 lignes, sans introduction ni conclusion) :
    📍 Emplacement : [Nom du fichier] -> [Nom de la fonction ou Numéro de ligne]
    ❌ Problème : [1 phrase décrivant l'erreur]
    💡 Correction : [Le code exact ou l'action précise à effectuer pour corriger]
    """

    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="openai/gpt-oss-120b",
            temperature=0.1,
        )

        print("💡 SYNTHÈSE IA :")
        print("--------------------------------------------------")
        print(chat_completion.choices[0].message.content)
        print("--------------------------------------------------")

    except Exception as e:
        print(f"Erreur lors de l'appel à l'API Groq : {e}")


def executer_commande(commande):
    resultat = subprocess.run(
        commande, capture_output=True, text=True, shell=True
    )
    return resultat.returncode, resultat.stdout + resultat.stderr


# --- DÉBUTER LA VÉRIFICATION ---
print("🔍 Vérification du code en cours...\n")
erreurs_detectees = ""

# 1. Vérification Mypy
code_mypy, sortie_mypy = executer_commande("python -m mypy calcul.py")
if code_mypy != 0:
    erreurs_detectees += f"--- ERREUR MYPY ---\n{sortie_mypy}\n"

# 2. Vérification Pytest
code_pytest, sortie_pytest = executer_commande("python -m pytest")
if code_pytest != 0:
    erreurs_detectees += f"--- ERREUR PYTEST ---\n{sortie_pytest}\n"

# 3. Traitement des résultats
if not erreurs_detectees:
    print("✅ TOUT EST PARFAIT ! Aucun bogue détecté.")
    sys.exit(0)
else:
    print("❌ Des erreurs ont été trouvées !")
    print(erreurs_detectees)

    # Appel de l'IA Groq
    demander_explication_ia(erreurs_detectees)
    sys.exit(1)