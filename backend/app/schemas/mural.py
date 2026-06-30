from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FotoCreate(BaseModel):
    url: str
    legenda: str | None = None


class FotoUpdate(BaseModel):
    url: str | None = None
    legenda: str | None = None


class FotoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    album_id: int
    url: str
    legenda: str | None


class AlbumCreate(BaseModel):
    nome: str


class AlbumUpdate(BaseModel):
    nome: str | None = None


class AlbumRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    evento_id: int
    nome: str
    fotos: list[FotoRead] = []


class PostagemCreate(BaseModel):
    texto: str


class ComentarioCreate(BaseModel):
    texto: str


class ComentarioRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    postagem_id: int
    autor_usuario_id: int
    texto: str
    data: datetime


class CurtidaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    postagem_id: int
    usuario_id: int
    data: datetime


class PostagemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    evento_id: int
    autor_usuario_id: int
    texto: str
    data_publicacao: datetime
    comentarios: list[ComentarioRead] = []
    curtidas: list[CurtidaRead] = []
