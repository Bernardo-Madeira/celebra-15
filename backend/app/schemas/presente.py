from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator


class PresenteCreate(BaseModel):
    nome: str
    descricao: str | None = None
    link_loja: str | None = None
    quantidade_maxima_contribuintes: int = 1

    @field_validator("quantidade_maxima_contribuintes")
    @classmethod
    def minimo_um(cls, v: int) -> int:
        if v < 1:
            raise ValueError("Deve ser >= 1")
        return v


class PresenteUpdate(BaseModel):
    nome: str | None = None
    descricao: str | None = None
    link_loja: str | None = None
    quantidade_maxima_contribuintes: int | None = None

    @field_validator("quantidade_maxima_contribuintes")
    @classmethod
    def minimo_um(cls, v: int | None) -> int | None:
        if v is not None and v < 1:
            raise ValueError("Deve ser >= 1")
        return v


class ReservaPresenteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    presente_id: int
    convidado_id: int
    data_reserva: datetime


class PresenteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    evento_id: int
    nome: str
    descricao: str | None
    link_loja: str | None
    quantidade_maxima_contribuintes: int
    reservas: list[ReservaPresenteRead] = []
