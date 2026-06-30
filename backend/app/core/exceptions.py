"""Exceções de domínio do sistema. Não importam nada do FastAPI."""


class DomainError(Exception):
    """Base para todas as exceções de domínio."""


class EmailJaCadastradoError(DomainError):
    pass


class CredenciaisInvalidasError(DomainError):
    pass


class UsuarioNaoEncontradoError(DomainError):
    pass


class TokenInvalidoError(DomainError):
    """Refresh token ou reset token não encontrado ou revogado."""


class TokenExpiradoError(DomainError):
    """Token válido mas com data de expiração no passado."""


class TokenJaUsadoError(DomainError):
    """Password reset token já foi utilizado."""


class SenhaAtualInvalidaError(DomainError):
    """Senha atual informada não confere ao alterar senha."""


class ConvidadoNaoEncontradoError(DomainError):
    pass


class EventoNaoEncontradoError(DomainError):
    pass


class AcessoNegadoError(DomainError):
    pass


class MesaNaoEncontradaError(DomainError):
    pass


class MesaLotadaError(DomainError):
    pass


class LimiteAcompanhantesExcedidoError(DomainError):
    pass


class PresenteNaoEncontradoError(DomainError):
    pass


class ReservaPresenteNaoEncontradaError(DomainError):
    pass


class ReservaPresenteJaExisteError(DomainError):
    """Convidado já contribuiu com este presente."""


class CotaPresenteEsgotadaError(DomainError):
    """Presente já atingiu a quantidade máxima de contribuintes."""


class FornecedorNaoEncontradoError(DomainError):
    pass


class PagamentoNaoEncontradoError(DomainError):
    pass


class ValorSinalInvalidoError(DomainError):
    """Valor do sinal não pode ser maior que o valor total do pagamento."""
