from sqlalchemy.orm import Session

from app.core.exceptions import HomenagemNaoEncontradaError
from app.models.cerimonial import Homenagem
from app.models.evento import Evento


def criar_homenagem(
    db: Session,
    evento: Evento,
    homenageado: str,
    texto: str,
    ordem: int,
    autor: str | None,
) -> Homenagem:
    homenagem = Homenagem(
        evento_id=evento.id,
        homenageado=homenageado,
        texto=texto,
        ordem=ordem,
        autor=autor,
    )
    db.add(homenagem)
    db.commit()
    db.refresh(homenagem)
    return homenagem


def listar_homenagens(db: Session, evento_id: int) -> list[Homenagem]:
    return (
        db.query(Homenagem)
        .filter(Homenagem.evento_id == evento_id)
        .order_by(Homenagem.ordem)
        .all()
    )


def buscar_homenagem(db: Session, homenagem_id: int, evento_id: int) -> Homenagem:
    homenagem = (
        db.query(Homenagem)
        .filter(Homenagem.id == homenagem_id, Homenagem.evento_id == evento_id)
        .first()
    )
    if homenagem is None:
        raise HomenagemNaoEncontradaError()
    return homenagem


def atualizar_homenagem(
    db: Session,
    homenagem: Homenagem,
    homenageado: str | None = None,
    texto: str | None = None,
    ordem: int | None = None,
    autor: str | None = None,
) -> Homenagem:
    if homenageado is not None:
        homenagem.homenageado = homenageado
    if texto is not None:
        homenagem.texto = texto
    if ordem is not None:
        homenagem.ordem = ordem
    if autor is not None:
        homenagem.autor = autor
    db.commit()
    db.refresh(homenagem)
    return homenagem


def excluir_homenagem(db: Session, homenagem: Homenagem) -> None:
    db.delete(homenagem)
    db.commit()
