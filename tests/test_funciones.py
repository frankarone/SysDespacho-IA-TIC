from funciones import clasificar_despacho


def test_clasifica_a_tiempo():
    assert clasificar_despacho(31) == "A_TIEMPO"


def test_clasifica_proximo():
    assert clasificar_despacho(30) == "PROXIMO"


def test_cero_minutos_sigue_proximo():
    assert clasificar_despacho(0) == "PROXIMO"


def test_clasifica_retrasado():
    assert clasificar_despacho(-1) == "RETRASADO"
