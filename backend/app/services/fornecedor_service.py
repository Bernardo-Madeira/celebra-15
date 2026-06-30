from datetime import date

from sqlalchemy.orm import Session

from app.core.exceptions import (
    FornecedorNaoEncontradoError,
    PagamentoNaoEncontradoError,
    ValorSinalInvalidoError,
)
from app.models.enums import StatusPagamento, TipoServicoFornecedor
from app.models.evento import Evento
from app.models.fornecedor import Fornecedor, Pagamento


# ---------------------------------------------------------------------------
# Fornecedores
# ---------------------------------------------------------------------------

def criar_fornecedor(
    db: Session,
    evento: Evento,
    nome: str,
    tipo_servico: TipoServicoFornecedor,
    contato_telefone: str,
    contato_email: str | None,
    observacoes: str | None,
) -> Fornecedor:
    fornecedor = Fornecedor(
        evento_id=evento.id,
        nome=nome,
        tipo_servico=tipo_servico,
        contato_telefone=contato_telefone,
        contato_email=contato_email,
        observacoes=observacoes,
    )
    db.add(fornecedor)
    db.commit()
    db.refresh(fornecedor)
    return fornecedor


def listar_fornecedores(db: Session, evento_id: int) -> list[Fornecedor]:
    return (
        db.query(Fornecedor)
        .filter(Fornecedor.evento_id == evento_id)
        .order_by(Fornecedor.nome)
        .all()
    )


def buscar_fornecedor(db: Session, fornecedor_id: int, evento_id: int) -> Fornecedor:
    fornecedor = (
        db.query(Fornecedor)
        .filter(Fornecedor.id == fornecedor_id, Fornecedor.evento_id == evento_id)
        .first()
    )
    if fornecedor is None:
        raise FornecedorNaoEncontradoError()
    return fornecedor


def atualizar_fornecedor(
    db: Session,
    fornecedor: Fornecedor,
    nome: str | None = None,
    tipo_servico: TipoServicoFornecedor | None = None,
    contato_telefone: str | None = None,
    contato_email: str | None = None,
    observacoes: str | None = None,
) -> Fornecedor:
    if nome is not None:
        fornecedor.nome = nome
    if tipo_servico is not None:
        fornecedor.tipo_servico = tipo_servico
    if contato_telefone is not None:
        fornecedor.contato_telefone = contato_telefone
    if contato_email is not None:
        fornecedor.contato_email = contato_email
    if observacoes is not None:
        fornecedor.observacoes = observacoes
    db.commit()
    db.refresh(fornecedor)
    return fornecedor


def excluir_fornecedor(db: Session, fornecedor: Fornecedor) -> None:
    db.delete(fornecedor)
    db.commit()


# ---------------------------------------------------------------------------
# Pagamentos
# ---------------------------------------------------------------------------

def _validar_sinal(valor_total: float, valor_sinal: float) -> None:
    if valor_sinal > valor_total:
        raise ValorSinalInvalidoError()


def criar_pagamento(
    db: Session,
    fornecedor: Fornecedor,
    valor_total: float,
    valor_sinal: float,
    data_sinal: date | None,
    data_vencimento_saldo: date,
    status_pagamento: StatusPagamento,
) -> Pagamento:
    _validar_sinal(valor_total, valor_sinal)
    pagamento = Pagamento(
        fornecedor_id=fornecedor.id,
        valor_total=valor_total,
        valor_sinal=valor_sinal,
        data_sinal=data_sinal,
        data_vencimento_saldo=data_vencimento_saldo,
        status_pagamento=status_pagamento,
    )
    db.add(pagamento)
    db.commit()
    db.refresh(pagamento)
    return pagamento


def listar_pagamentos(db: Session, fornecedor_id: int) -> list[Pagamento]:
    return (
        db.query(Pagamento)
        .filter(Pagamento.fornecedor_id == fornecedor_id)
        .order_by(Pagamento.data_vencimento_saldo)
        .all()
    )


def buscar_pagamento(db: Session, pagamento_id: int, fornecedor_id: int) -> Pagamento:
    pagamento = (
        db.query(Pagamento)
        .filter(Pagamento.id == pagamento_id, Pagamento.fornecedor_id == fornecedor_id)
        .first()
    )
    if pagamento is None:
        raise PagamentoNaoEncontradoError()
    return pagamento


def atualizar_pagamento(
    db: Session,
    pagamento: Pagamento,
    valor_total: float | None = None,
    valor_sinal: float | None = None,
    data_sinal: date | None = None,
    data_vencimento_saldo: date | None = None,
    status_pagamento: StatusPagamento | None = None,
) -> Pagamento:
    novo_total = valor_total if valor_total is not None else float(pagamento.valor_total)
    novo_sinal = valor_sinal if valor_sinal is not None else float(pagamento.valor_sinal)
    _validar_sinal(novo_total, novo_sinal)

    if valor_total is not None:
        pagamento.valor_total = valor_total
    if valor_sinal is not None:
        pagamento.valor_sinal = valor_sinal
    if data_sinal is not None:
        pagamento.data_sinal = data_sinal
    if data_vencimento_saldo is not None:
        pagamento.data_vencimento_saldo = data_vencimento_saldo
    if status_pagamento is not None:
        pagamento.status_pagamento = status_pagamento
    db.commit()
    db.refresh(pagamento)
    return pagamento


def excluir_pagamento(db: Session, pagamento: Pagamento) -> None:
    db.delete(pagamento)
    db.commit()
