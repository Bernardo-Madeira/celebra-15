from pydantic import BaseModel, ConfigDict

from app.models.enums import StatusConfirmacao


class MesaCreate(BaseModel):
    numero: int
    capacidade: int


class MesaUpdate(BaseModel):
    numero: int | None = None
    capacidade: int | None = None


class MesaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    evento_id: int
    numero: int
    capacidade: int


class AcompanhanteCreate(BaseModel):
    nome: str


class AcompanhanteUpdate(BaseModel):
    nome: str | None = None


class AcompanhanteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    convidado_id: int
    nome: str


class ConvidadoCreate(BaseModel):
    nome: str
    email: str
    telefone: str


class ConvidadoUpdate(BaseModel):
    nome: str | None = None
    telefone: str | None = None
    mesa_id: int | None = None


class ConvidadoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    evento_id: int
    usuario_id: int
    nome: str
    telefone: str
    token_confirmacao: str
    status_confirmacao: StatusConfirmacao
    mesa_id: int | None
    acompanhantes: list[AcompanhanteRead] = []


class ConfirmarPresencaBody(BaseModel):
    status_confirmacao: StatusConfirmacao
    acompanhantes: list[str] = []
