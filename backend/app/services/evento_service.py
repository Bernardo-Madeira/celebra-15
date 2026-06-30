from datetime import datetime

from sqlalchemy.orm import Session

from app.core.exceptions import AcessoNegadoError, EventoNaoEncontradoError
from app.models.enums import TipoPerfil
from app.models.evento import Evento
from app.models.usuario import Usuario


def _verificar_acesso(evento: Evento, usuario: Usuario) -> None:
    """
    Organizador só acessa seus próprios eventos; cerimonialista acessa todos;
    convidado só acessa o evento ao qual está vinculado.
    """
    if usuario.tipo_perfil == TipoPerfil.ORGANIZADOR and evento.usuario_organizador_id != usuario.id:
        raise AcessoNegadoError()
    if usuario.tipo_perfil == TipoPerfil.CONVIDADO and (
        usuario.convidado is None or usuario.convidado.evento_id != evento.id
    ):
        raise AcessoNegadoError()


def criar_evento(
    db: Session,
    usuario: Usuario,
    nome_debutante: str,
    data_evento: datetime,
    local: str,
    max_acompanhantes: int,
) -> Evento:
    evento = Evento(
        nome_debutante=nome_debutante,
        data_evento=data_evento,
        local=local,
        max_acompanhantes_por_convidado=max_acompanhantes,
        usuario_organizador_id=usuario.id,
    )
    db.add(evento)
    db.commit()
    db.refresh(evento)
    return evento


def listar_eventos(db: Session, usuario: Usuario) -> list[Evento]:
    q = db.query(Evento)
    if usuario.tipo_perfil == TipoPerfil.ORGANIZADOR:
        q = q.filter(Evento.usuario_organizador_id == usuario.id)
    return q.order_by(Evento.data_evento).all()


def buscar_evento(db: Session, evento_id: int, usuario: Usuario) -> Evento:
    evento = db.get(Evento, evento_id)
    if evento is None:
        raise EventoNaoEncontradoError()
    _verificar_acesso(evento, usuario)
    return evento


def atualizar_evento(
    db: Session,
    evento: Evento,
    nome_debutante: str | None = None,
    data_evento: datetime | None = None,
    local: str | None = None,
    max_acompanhantes: int | None = None,
) -> Evento:
    if nome_debutante is not None:
        evento.nome_debutante = nome_debutante
    if data_evento is not None:
        evento.data_evento = data_evento
    if local is not None:
        evento.local = local
    if max_acompanhantes is not None:
        evento.max_acompanhantes_por_convidado = max_acompanhantes
    db.commit()
    db.refresh(evento)
    return evento


def excluir_evento(db: Session, evento: Evento) -> None:
    db.delete(evento)
    db.commit()
