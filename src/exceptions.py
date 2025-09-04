class ParserBaseException(Exception):
    """Базовое исключение для всех ошибок парсера."""


class ParserFindTagException(ParserBaseException):
    """Вызывается, когда парсер не может найти тег."""


class RequestErrorException(ParserBaseException):
    """Вызывается при ошибках HTTP-запросов."""
