def clasificar_despacho(minutos_restantes):
    """
    Clasifica un despacho según los minutos restantes.

    Args:
        minutos_restantes: Cantidad de minutos antes o después
        de la hora programada.

    Returns:
        El estado A_TIEMPO, PROXIMO o RETRASADO.
    """
    if minutos_restantes > 30:
        return "A_TIEMPO"

    if minutos_restantes >= 0:
        return "PROXIMO"

    return "RETRASADO"