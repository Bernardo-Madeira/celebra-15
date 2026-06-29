"""Exceções de domínio do sistema. Não importam nada do FastAPI."""


class DomainError(Exception):
    """Base para todas as exceções de domínio."""


class EmailJaCadastradoError(DomainError):
    pass


class CredenciaisInvalidasError(DomainError):
    pass


class UsuarioNaoEncontradoError(DomainError):
    pass
