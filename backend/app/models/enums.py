"""Enums Python mapeados para colunas Enum do SQLAlchemy/MySQL."""

import enum


class TipoPerfil(str, enum.Enum):
    ORGANIZADOR = "organizador"
    CERIMONIALISTA = "cerimonialista"
    CONVIDADO = "convidado"


class StatusConfirmacao(str, enum.Enum):
    PENDENTE = "pendente"
    CONFIRMADO = "confirmado"
    RECUSADO = "recusado"


class TipoServicoFornecedor(str, enum.Enum):
    BUFFET = "buffet"
    DECORACAO = "decoracao"
    FOTOGRAFIA = "fotografia"
    SOM_ILUMINACAO = "som_iluminacao"
    SEGURANCA = "seguranca"
    OUTRO = "outro"


class StatusPagamento(str, enum.Enum):
    PENDENTE = "pendente"
    PARCIAL = "parcial"
    PAGO = "pago"


class StatusTarefa(str, enum.Enum):
    PENDENTE = "pendente"
    EM_ANDAMENTO = "em_andamento"
    CONCLUIDA = "concluida"


class DestinatarioAviso(str, enum.Enum):
    CERIMONIALISTA = "cerimonialista"
    EQUIPE_INTERNA = "equipe_interna"
    TODOS = "todos"
