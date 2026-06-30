from sqlalchemy.orm import Session

from app.core.exceptions import AvisoNaoEncontradoError
from app.models.aviso import Aviso
from app.models.enums import DestinatarioAviso
from app.models.evento import Evento


def criar_aviso(
    db: Session,
    evento: Evento,
    titulo: str,
    mensagem: str,
    destinatario_tipo: DestinatarioAviso,
) -> Aviso:
    aviso = Aviso(
        evento_id=evento.id,
        titulo=titulo,
        mensagem=mensagem,
        destinatario_tipo=destinatario_tipo,
    )
    db.add(aviso)
    db.commit()
    db.refresh(aviso)
    return aviso


def listar_avisos(db: Session, evento_id: int) -> list[Aviso]:
    return (
        db.query(Aviso)
        .filter(Aviso.evento_id == evento_id)
        .order_by(Aviso.data_publicacao.desc())
        .all()
    )


def buscar_aviso(db: Session, aviso_id: int, evento_id: int) -> Aviso:
    aviso = (
        db.query(Aviso)
        .filter(Aviso.id == aviso_id, Aviso.evento_id == evento_id)
        .first()
    )
    if aviso is None:
        raise AvisoNaoEncontradoError()
    return aviso


def atualizar_aviso(
    db: Session,
    aviso: Aviso,
    titulo: str | None = None,
    mensagem: str | None = None,
    destinatario_tipo: DestinatarioAviso | None = None,
) -> Aviso:
    if titulo is not None:
        aviso.titulo = titulo
    if mensagem is not None:
        aviso.mensagem = mensagem
    if destinatario_tipo is not None:
        aviso.destinatario_tipo = destinatario_tipo
    db.commit()
    db.refresh(aviso)
    return aviso


def excluir_aviso(db: Session, aviso: Aviso) -> None:
    db.delete(aviso)
    db.commit()
