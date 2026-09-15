from typing import List


class Calculatrice:

    def __init__(self, utilisateur: str) -> None:
        self.utilisateur = utilisateur
        self.historique: List[str] = []

    def diviser(self, a: float, b: float) -> float:
        """Divise a par b avec gestion de la division par zéro."""
        if b == 0:
            raise ValueError("Impossible de diviser par zéro !")
        resultat = a / b
        self.historique.append(f"{a} / {b} = {resultat}")
        return resultat

    def calculer_moyenne(self, notes: List[float]) -> float:
        """Calcule la moyenne d'une liste de notes."""
        if not notes:
            return 0.0

        total = sum(notes)
        moyenne = total / len(notes)

        # ⚠️ ERREUR DE TYPAGE INTENTIONNELLE POUR MYPY ⚠️
        # On a indiqué dans le header (-> float) qu'on retournait un float,
        # mais ici on retourne du texte (str) avec le symbole "%" !
        resultat_incorrect: str = f"{moyenne:.2f}%"

        return valeur