from datetime import date

from pydantic import BaseModel, ConfigDict

from app.models.enums import StatusTarefa


class TarefaCreate(BaseModel):
    titulo: str
    descricao: str | None = None
    data_prazo: date
    responsavel: str
    status: StatusTarefa = StatusTarefa.PENDENTE


class TarefaUpdate(BaseModel):
    titulo: str | None = None
    descricao: str | None = None
    data_prazo: date | None = None
    responsavel: str | None = None
    status: StatusTarefa | None = None


class TarefaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    evento_id: int
    titulo: str
    descricao: str | None
    data_prazo: date
    responsavel: str
    status: StatusTarefa
