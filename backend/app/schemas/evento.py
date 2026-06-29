from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator


class EventoCreate(BaseModel):
    nome_debutante: str
    data_evento: datetime
    local: str
    max_acompanhantes_por_convidado: int = 0

    @field_validator("max_acompanhantes_por_convidado")
    @classmethod
    def nao_negativo(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Deve ser >= 0")
        return v


class EventoUpdate(BaseModel):
    nome_debutante: str | None = None
    data_evento: datetime | None = None
    local: str | None = None
    max_acompanhantes_por_convidado: int | None = None

    @field_validator("max_acompanhantes_por_convidado")
    @classmethod
    def nao_negativo(cls, v: int | None) -> int | None:
        if v is not None and v < 0:
            raise ValueError("Deve ser >= 0")
        return v


class EventoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome_debutante: str
    data_evento: datetime
    local: str
    max_acompanhantes_por_convidado: int
    usuario_organizador_id: int
