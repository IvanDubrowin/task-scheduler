class InvalidStateError(Exception):
    """
    Ошибка при попытке отменить задачу в завершенном или выполненом состоянии
    """
