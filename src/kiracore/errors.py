class KiraCoreError(Exception):
    """Базовое исключение среды Кира:Ядра."""


class GenomeIntegrityError(KiraCoreError):
    """Геном не прошёл проверку целостности или структуры."""


class AuthorizationError(KiraCoreError):
    """Операция требует подтверждённой авторизации Алека."""


class ProtocolViolation(KiraCoreError):
    """Результат или переход состояния нарушает обязательный протокол."""
