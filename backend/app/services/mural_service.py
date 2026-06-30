from sqlalchemy.orm import Session

from app.core.exceptions import (
    AcessoNegadoError,
    AlbumNaoEncontradoError,
    ComentarioNaoEncontradoError,
    CurtidaJaExisteError,
    CurtidaNaoEncontradaError,
    FotoNaoEncontradaError,
    PostagemNaoEncontradaError,
)
from app.models.evento import Evento
from app.models.mural import Album, Comentario, Curtida, Foto, Postagem
from app.models.usuario import Usuario


def _pode_moderar(evento: Evento, autor_usuario_id: int, usuario: Usuario) -> bool:
    """Autor do conteúdo ou organizador do evento podem excluí-lo."""
    return usuario.id == autor_usuario_id or evento.usuario_organizador_id == usuario.id


# ---------------------------------------------------------------------------
# Álbuns (gestão restrita ao organizador)
# ---------------------------------------------------------------------------

def criar_album(db: Session, evento: Evento, nome: str) -> Album:
    album = Album(evento_id=evento.id, nome=nome)
    db.add(album)
    db.commit()
    db.refresh(album)
    return album


def listar_albuns(db: Session, evento_id: int) -> list[Album]:
    return db.query(Album).filter(Album.evento_id == evento_id).order_by(Album.nome).all()


def buscar_album(db: Session, album_id: int, evento_id: int) -> Album:
    album = (
        db.query(Album)
        .filter(Album.id == album_id, Album.evento_id == evento_id)
        .first()
    )
    if album is None:
        raise AlbumNaoEncontradoError()
    return album


def atualizar_album(db: Session, album: Album, nome: str | None = None) -> Album:
    if nome is not None:
        album.nome = nome
    db.commit()
    db.refresh(album)
    return album


def excluir_album(db: Session, album: Album) -> None:
    db.delete(album)
    db.commit()


# ---------------------------------------------------------------------------
# Fotos (gestão restrita ao organizador)
# ---------------------------------------------------------------------------

def criar_foto(db: Session, album: Album, url: str, legenda: str | None) -> Foto:
    foto = Foto(album_id=album.id, url=url, legenda=legenda)
    db.add(foto)
    db.commit()
    db.refresh(foto)
    return foto


def listar_fotos(db: Session, album_id: int) -> list[Foto]:
    return db.query(Foto).filter(Foto.album_id == album_id).order_by(Foto.id).all()


def buscar_foto(db: Session, foto_id: int, album_id: int) -> Foto:
    foto = (
        db.query(Foto)
        .filter(Foto.id == foto_id, Foto.album_id == album_id)
        .first()
    )
    if foto is None:
        raise FotoNaoEncontradaError()
    return foto


def atualizar_foto(
    db: Session, foto: Foto, url: str | None = None, legenda: str | None = None
) -> Foto:
    if url is not None:
        foto.url = url
    if legenda is not None:
        foto.legenda = legenda
    db.commit()
    db.refresh(foto)
    return foto


def excluir_foto(db: Session, foto: Foto) -> None:
    db.delete(foto)
    db.commit()


# ---------------------------------------------------------------------------
# Postagens (mural — qualquer usuário do evento pode publicar)
# ---------------------------------------------------------------------------

def criar_postagem(db: Session, evento: Evento, autor: Usuario, texto: str) -> Postagem:
    postagem = Postagem(evento_id=evento.id, autor_usuario_id=autor.id, texto=texto)
    db.add(postagem)
    db.commit()
    db.refresh(postagem)
    return postagem


def listar_postagens(db: Session, evento_id: int) -> list[Postagem]:
    return (
        db.query(Postagem)
        .filter(Postagem.evento_id == evento_id)
        .order_by(Postagem.data_publicacao.desc(), Postagem.id.desc())
        .all()
    )


def buscar_postagem(db: Session, postagem_id: int, evento_id: int) -> Postagem:
    postagem = (
        db.query(Postagem)
        .filter(Postagem.id == postagem_id, Postagem.evento_id == evento_id)
        .first()
    )
    if postagem is None:
        raise PostagemNaoEncontradaError()
    return postagem


def excluir_postagem(db: Session, postagem: Postagem, usuario: Usuario) -> None:
    if not _pode_moderar(postagem.evento, postagem.autor_usuario_id, usuario):
        raise AcessoNegadoError()
    db.delete(postagem)
    db.commit()


# ---------------------------------------------------------------------------
# Comentários
# ---------------------------------------------------------------------------

def criar_comentario(db: Session, postagem: Postagem, autor: Usuario, texto: str) -> Comentario:
    comentario = Comentario(postagem_id=postagem.id, autor_usuario_id=autor.id, texto=texto)
    db.add(comentario)
    db.commit()
    db.refresh(comentario)
    return comentario


def listar_comentarios(db: Session, postagem_id: int) -> list[Comentario]:
    return (
        db.query(Comentario)
        .filter(Comentario.postagem_id == postagem_id)
        .order_by(Comentario.data)
        .all()
    )


def buscar_comentario(db: Session, comentario_id: int, postagem_id: int) -> Comentario:
    comentario = (
        db.query(Comentario)
        .filter(Comentario.id == comentario_id, Comentario.postagem_id == postagem_id)
        .first()
    )
    if comentario is None:
        raise ComentarioNaoEncontradoError()
    return comentario


def excluir_comentario(db: Session, comentario: Comentario, usuario: Usuario) -> None:
    evento = comentario.postagem.evento
    if not _pode_moderar(evento, comentario.autor_usuario_id, usuario):
        raise AcessoNegadoError()
    db.delete(comentario)
    db.commit()


# ---------------------------------------------------------------------------
# Curtidas
# ---------------------------------------------------------------------------

def curtir_postagem(db: Session, postagem: Postagem, usuario: Usuario) -> Curtida:
    ja_curtiu = (
        db.query(Curtida)
        .filter(Curtida.postagem_id == postagem.id, Curtida.usuario_id == usuario.id)
        .first()
    )
    if ja_curtiu is not None:
        raise CurtidaJaExisteError()

    curtida = Curtida(postagem_id=postagem.id, usuario_id=usuario.id)
    db.add(curtida)
    db.commit()
    db.refresh(curtida)
    return curtida


def descurtir_postagem(db: Session, postagem: Postagem, usuario: Usuario) -> None:
    curtida = (
        db.query(Curtida)
        .filter(Curtida.postagem_id == postagem.id, Curtida.usuario_id == usuario.id)
        .first()
    )
    if curtida is None:
        raise CurtidaNaoEncontradaError()
    db.delete(curtida)
    db.commit()
