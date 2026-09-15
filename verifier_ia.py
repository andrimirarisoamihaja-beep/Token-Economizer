import os
import subprocess
import sys
from groq import Groq


def demander_explication_ia(erreurs: str):
    """Envoie l'erreur à Groq (gpt-oss-120b) et affiche son explication."""
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        print(
            "⚠️ Clé GROQ_API_KEY non détectée. L'analyse IA est désactivée."
        )
        return

    client = Groq(api_key=api_key)

    print(
        "\n⚡ L'IA (Groq - gpt-oss-120b) analyse vos erreurs à toute vitesse...\n"
    )

    prompt = f"""
    Tu es un assistant professeur de Python bienveillant et expert.
    Voici des erreurs détectées par Mypy ou Pytest :

    ```text
    {erreurs}
    ```

    Consignes :
    1. Explique l'erreur en français simple (1 ou 2 phrases max).
    2. Explique POURQUOI cette erreur s'est produite.
    3. Donne le code exact pour la corriger.
    """

    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="openai/gpt-oss-120b",  # Modèle gratuit et très puissant
            temperature=0.2,
        )

        print("💡 EXPLICATION DE L'IA (Groq) :")
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