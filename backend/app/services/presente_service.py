from sqlalchemy.orm import Session

from app.core.exceptions import (
    ConvidadoNaoEncontradoError,
    CotaPresenteEsgotadaError,
    PresenteNaoEncontradoError,
    ReservaPresenteJaExisteError,
    ReservaPresenteNaoEncontradaError,
)
from app.models.convidado import Convidado
from app.models.evento import Evento
from app.models.presente import Presente, ReservaPresente


# ---------------------------------------------------------------------------
# Presentes (CRUD autenticado)
# ---------------------------------------------------------------------------

def criar_presente(
    db: Session,
    evento: Evento,
    nome: str,
    descricao: str | None,
    link_loja: str | None,
    quantidade_maxima_contribuintes: int,
) -> Presente:
    presente = Presente(
        evento_id=evento.id,
        nome=nome,
        descricao=descricao,
        link_loja=link_loja,
        quantidade_maxima_contribuintes=quantidade_maxima_contribuintes,
    )
    db.add(presente)
    db.commit()
    db.refresh(presente)
    return presente


def listar_presentes(db: Session, evento_id: int) -> list[Presente]:
    return (
        db.query(Presente)
        .filter(Presente.evento_id == evento_id)
        .order_by(Presente.nome)
        .all()
    )


def buscar_presente(db: Session, presente_id: int, evento_id: int) -> Presente:
    presente = (
        db.query(Presente)
        .filter(Presente.id == presente_id, Presente.evento_id == evento_id)
        .first()
    )
    if presente is None:
        raise PresenteNaoEncontradoError()
    return presente


def atualizar_presente(
    db: Session,
    presente: Presente,
    nome: str | None = None,
    descricao: str | None = None,
    link_loja: str | None = None,
    quantidade_maxima_contribuintes: int | None = None,
) -> Presente:
    if nome is not None:
        presente.nome = nome
    if descricao is not None:
        presente.descricao = descricao
    if link_loja is not None:
        presente.link_loja = link_loja
    if quantidade_maxima_contribuintes is not None:
        presente.quantidade_maxima_contribuintes = quantidade_maxima_contribuintes
    db.commit()
    db.refresh(presente)
    return presente


def excluir_presente(db: Session, presente: Presente) -> None:
    db.delete(presente)
    db.commit()


# ---------------------------------------------------------------------------
# Reservas (acesso público via token_confirmacao do convidado)
# ---------------------------------------------------------------------------

def buscar_convidado_por_token(db: Session, token: str) -> Convidado:
    convidado = db.query(Convidado).filter(Convidado.token_confirmacao == token).first()
    if convidado is None:
        raise ConvidadoNaoEncontradoError()
    return convidado


def listar_presentes_do_convidado(db: Session, token: str) -> list[Presente]:
    convidado = buscar_convidado_por_token(db, token)
    return listar_presentes(db, convidado.evento_id)


def reservar_presente(db: Session, token: str, presente_id: int) -> ReservaPresente:
    convidado = buscar_convidado_por_token(db, token)
    presente = buscar_presente(db, presente_id, convidado.evento_id)

    ja_reservou = (
        db.query(ReservaPresente)
        .filter(
            ReservaPresente.presente_id == presente.id,
            ReservaPresente.convidado_id == convidado.id,
        )
        .first()
    )
    if ja_reservou is not None:
        raise ReservaPresenteJaExisteError()

    total_reservas = (
        db.query(ReservaPresente).filter(ReservaPresente.presente_id == presente.id).count()
    )
    if total_reservas >= presente.quantidade_maxima_contribuintes:
        raise CotaPresenteEsgotadaError()

    reserva = ReservaPresente(presente_id=presente.id, convidado_id=convidado.id)
    db.add(reserva)
    db.commit()
    db.refresh(reserva)
    return reserva


def cancelar_reserva(db: Session, token: str, presente_id: int) -> None:
    convidado = buscar_convidado_por_token(db, token)
    reserva = (
        db.query(ReservaPresente)
        .filter(
            ReservaPresente.presente_id == presente_id,
            ReservaPresente.convidado_id == convidado.id,
        )
        .first()
    )
    if reserva is None:
        raise ReservaPresenteNaoEncontradaError()
    db.delete(reserva)
    db.commit()
