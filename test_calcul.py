from calcul import addition

def test_addition_correcte():
    assert addition(2, 3) == 5  # Ce test va réussir

def test_addition_erreur():
    assert addition(2, 2) == 5  # Ce test va échouer exprès pour essayer
