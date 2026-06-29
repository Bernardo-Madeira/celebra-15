from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import TipoPerfil


class UsuarioCreate(BaseModel):
    nome: str
    email: str
    senha: str


class UsuarioUpdate(BaseModel):
    nome: str | None = None
    senha: str | None = None


class UsuarioRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    email: str
    tipo_perfil: TipoPerfil
    data_criacao: datetime


class TokenRead(BaseModel):
    access_token: str
    token_type: str = "bearer"
