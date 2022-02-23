"""Модуль ошибок."""


class APIValueException(Exception):
    """Ошибка если API недоступен."""

    pass


class EmptyDictException(Exception):
    """Ошибка если отсутствуют работы в списке доманшних работ."""

    pass
