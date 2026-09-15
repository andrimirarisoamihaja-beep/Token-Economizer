import pytest
from calcul import Calculatrice


# Fixture pour éviter de recréer l'objet à chaque test
@pytest.fixture
def ma_calculatrice():
    return Calculatrice("Alice")


def test_division_valide(ma_calculatrice):
    assert ma_calculatrice.diviser(10, 2) == 5.0


def test_division_par_zero(ma_calculatrice):
    # Vérifie que le code lève bien une erreur quand b = 0
    with pytest.raises(ValueError, match="Impossible de diviser par zéro !"):
        ma_calculatrice.diviser(10, 0)


def test_calculer_moyenne(ma_calculatrice):
    notes = [10.0, 15.0, 20.0]
    # Ce test s'attend à recevoir un nombre (15.0)
    assert ma_calculatrice.calculer_moyenne(notes) == 15.0