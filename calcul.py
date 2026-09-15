class Calculatrice:
    def __init__(self, utilisateur: str) -> None:
        self.utilisateur = utilisateur
        self.historique: list[str] = []

    def diviser(self, a: float, b: float) -> float:
        if b == 0:
            raise ValueError("Impossible de diviser par zéro !")

        resultat = a / b
        self.historique.append(f"{a} / {b} = {resultat}")
        return resultat

    def calculer_moyenne(self, notes: list[float]) -> float:
        if not notes:
            return 0.0

        total = sum(notes)
        moyenne = total / len(notes)
        return moyenne