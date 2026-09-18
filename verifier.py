import subprocess
import sys


def executer_commande(commande):
    resultat = subprocess.run(
        commande,
        capture_output=True,
        text=True,
        shell=True,
        check=False   # <-- ajout obligatoire
    )
    return resultat


print("=" * 60)
print("🤖 ASSISTANT DE VÉRIFICATION DE CODE")
print("=" * 60 + "\n")

code_erreur = 0

# --- 1. VÉRIFICATION DES TYPES (MYPY) ---
print("🔍 1. Analyse des types avec Mypy...")
code, sortie = executer_commande("python -m mypy calcul.py")

if code == 0:
    print("✅ Bravo ! Tous les types de variables sont respectés.\n")
else:
    code_erreur = 1
    print("❌ ATTENTION : Erreur de typage détectée !")
    if "Incompatible return value type" in sortie:
        print("💡 Explication : Une fonction ne renvoie pas le bon type.")
        print(
            "👉 Suggestion : Vérifiez ce que votre fonction retourne (ex: du texte 'str' au lieu d'un nombre 'float')."
        )
    print("\n--- Détail technique ---")
    print(sortie)

# --- 2. TESTS UNITAIRES (PYTEST) ---
print("-" * 60)
print("🧪 2. Exécution des tests unitaires avec Pytest...")
code, sortie = executer_commande("python -m pytest")

if code == 0:
    print("✅ Bravo ! Tous les tests unitaires sont passés avec succès.\n")
else:
    code_erreur = 1
    print("❌ ATTENTION : Au moins un test a échoué !")
    if "AssertionError" in sortie:
        print("💡 Explication : Le résultat calculé ne correspond pas à ce qui était attendu.")
        print(
            "👉 Suggestion : Regardez les valeurs comparées dans 'test_calcul.py' avec 'assert'."
        )
    print("\n--- Détail technique ---")
    print(sortie)

print("=" * 60)
if code_erreur == 0:
    print("🎉 TOUT EST PARFAIT ! Vous pouvez pousser votre code sur GitHub.")
else:
    print("⚠️ Corrigez les erreurs ci-dessus avant de pousser votre code.")
print("=" * 60)

sys.exit(code_erreur)