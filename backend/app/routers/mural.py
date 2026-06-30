from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_usuario, require_organizador
from app.db.database import get_db
from app.models.usuario import Usuario
from app.schemas.mural import (
    AlbumCreate,
    AlbumRead,
    AlbumUpdate,
    ComentarioCreate,
    ComentarioRead,
    CurtidaRead,
    FotoCreate,
    FotoRead,
    FotoUpdate,
    PostagemCreate,
    PostagemRead,
)
from app.services.evento_service import buscar_evento
from app.services.mural_service import (
    atualizar_album,
    atualizar_foto,
    buscar_album,
    buscar_comentario,
    buscar_foto,
    buscar_postagem,
    criar_album,
    criar_comentario,
    criar_foto,
    criar_postagem,
    curtir_postagem,
    descurtir_postagem,
    excluir_album,
    excluir_comentario,
    excluir_foto,
    excluir_postagem,
    listar_albuns,
    listar_comentarios,
    listar_fotos,
    listar_postagens,
)

# Álbuns e fotos: gestão restrita ao organizador, leitura por qualquer participante do evento.
album_router = APIRouter(prefix="/eventos/{evento_id}/albuns", tags=["mural - álbuns"])

# Mural: postagens, comentários e curtidas — acessível a qualquer participante autenticado do evento.
postagem_router = APIRouter(prefix="/eventos/{evento_id}/postagens", tags=["mural - postagens"])


# ---------------------------------------------------------------------------
# Álbuns
# ---------------------------------------------------------------------------

@album_router.post("", response_model=AlbumRead, status_code=201)
def criar_album_route(
    evento_id: int,
    body: AlbumCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_organizador),
):
    evento = buscar_evento(db, evento_id, usuario)
    return criar_album(db, evento, body.nome)


@album_router.get("", response_model=list[AlbumRead])
def listar_albuns_route(
    evento_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_usuario),
):
    buscar_evento(db, evento_id, usuario)
    return listar_albuns(db, evento_id)


@album_router.get("/{album_id}", response_model=AlbumRead)
def obter_album(
    evento_id: int,
    album_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_usuario),
):
    buscar_evento(db, evento_id, usuario)
    return buscar_album(db, album_id, evento_id)


@album_router.patch("/{album_id}", response_model=AlbumRead)
def atualizar_album_route(
    evento_id: int,
    album_id: int,
    body: AlbumUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_organizador),
):
    buscar_evento(db, evento_id, usuario)
    album = buscar_album(db, album_id, evento_id)
    return atualizar_album(db, album, body.nome)


@album_router.delete("/{album_id}", status_code=204)
def excluir_album_route(
    evento_id: int,
    album_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_organizador),
):
    buscar_evento(db, evento_id, usuario)
    album = buscar_album(db, album_id, evento_id)
    excluir_album(db, album)


# ---------------------------------------------------------------------------
# Fotos
# ---------------------------------------------------------------------------

@album_router.post("/{album_id}/fotos", response_model=FotoRead, status_code=201)
def criar_foto_route(
    evento_id: int,
    album_id: int,
    body: FotoCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_organizador),
):
    buscar_evento(db, evento_id, usuario)
    album = buscar_album(db, album_id, evento_id)
    return criar_foto(db, album, body.url, body.legenda)


@album_router.get("/{album_id}/fotos", response_model=list[FotoRead])
def listar_fotos_route(
    evento_id: int,
    album_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_usuario),
):
    buscar_evento(db, evento_id, usuario)
    buscar_album(db, album_id, evento_id)
    return listar_fotos(db, album_id)


@album_router.get("/{album_id}/fotos/{foto_id}", response_model=FotoRead)
def obter_foto(
    evento_id: int,
    album_id: int,
    foto_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_usuario),
):
    buscar_evento(db, evento_id, usuario)
    buscar_album(db, album_id, evento_id)
    return buscar_foto(db, foto_id, album_id)


@album_router.patch("/{album_id}/fotos/{foto_id}", response_model=FotoRead)
def atualizar_foto_route(
    evento_id: int,
    album_id: int,
    foto_id: int,
    body: FotoUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_organizador),
):
    buscar_evento(db, evento_id, usuario)
    buscar_album(db, album_id, evento_id)
    foto = buscar_foto(db, foto_id, album_id)
    return atualizar_foto(db, foto, body.url, body.legenda)


@album_router.delete("/{album_id}/fotos/{foto_id}", status_code=204)
def excluir_foto_route(
    evento_id: int,
    album_id: int,
    foto_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_organizador),
):
    buscar_evento(db, evento_id, usuario)
    buscar_album(db, album_id, evento_id)
    foto = buscar_foto(db, foto_id, album_id)
    excluir_foto(db, foto)


# ---------------------------------------------------------------------------
# Postagens
# ---------------------------------------------------------------------------

@postagem_router.post("", response_model=PostagemRead, status_code=201)
def criar_postagem_route(
    evento_id: int,
    body: PostagemCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_usuario),
):
    evento = buscar_evento(db, evento_id, usuario)
    return criar_postagem(db, evento, usuario, body.texto)


@postagem_router.get("", response_model=list[PostagemRead])
def listar_postagens_route(
    evento_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_usuario),
):
    buscar_evento(db, evento_id, usuario)
    return listar_postagens(db, evento_id)


@postagem_router.get("/{postagem_id}", response_model=PostagemRead)
def obter_postagem(
    evento_id: int,
    postagem_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_usuario),
):
    buscar_evento(db, evento_id, usuario)
    return buscar_postagem(db, postagem_id, evento_id)


@postagem_router.delete("/{postagem_id}", status_code=204)
def excluir_postagem_route(
    evento_id: int,
    postagem_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_usuario),
):
    buscar_evento(db, evento_id, usuario)
    postagem = buscar_postagem(db, postagem_id, evento_id)
    excluir_postagem(db, postagem, usuario)


# ---------------------------------------------------------------------------
# Comentários
# ---------------------------------------------------------------------------

@postagem_router.post("/{postagem_id}/comentarios", response_model=ComentarioRead, status_code=201)
def criar_comentario_route(
    evento_id: int,
    postagem_id: int,
    body: ComentarioCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_usuario),
):
    buscar_evento(db, evento_id, usuario)
    postagem = buscar_postagem(db, postagem_id, evento_id)
    return criar_comentario(db, postagem, usuario, body.texto)


@postagem_router.get("/{postagem_id}/comentarios", response_model=list[ComentarioRead])
def listar_comentarios_route(
    evento_id: int,
    postagem_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_usuario),
):
    buscar_evento(db, evento_id, usuario)
    buscar_postagem(db, postagem_id, evento_id)
    return listar_comentarios(db, postagem_id)


@postagem_router.delete("/{postagem_id}/comentarios/{comentario_id}", status_code=204)
def excluir_comentario_route(
    evento_id: int,
    postagem_id: int,
    comentario_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_usuario),
):
    buscar_evento(db, evento_id, usuario)
    buscar_postagem(db, postagem_id, evento_id)
    comentario = buscar_comentario(db, comentario_id, postagem_id)
    excluir_comentario(db, comentario, usuario)


# ---------------------------------------------------------------------------
# Curtidas
# ---------------------------------------------------------------------------

@postagem_router.post("/{postagem_id}/curtir", response_model=CurtidaRead, status_code=201)
def curtir_postagem_route(
    evento_id: int,
    postagem_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_usuario),
):
    buscar_evento(db, evento_id, usuario)
    postagem = buscar_postagem(db, postagem_id, evento_id)
    return curtir_postagem(db, postagem, usuario)


@postagem_router.delete("/{postagem_id}/curtir", status_code=204)
def descurtir_postagem_route(
    evento_id: int,
    postagem_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_usuario),
):
    buscar_evento(db, evento_id, usuario)
    postagem = buscar_postagem(db, postagem_id, evento_id)
    descurtir_postagem(db, postagem, usuario)
