from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import DestinatarioAviso


class AvisoCreate(BaseModel):
    titulo: str
    mensagem: str
    destinatario_tipo: DestinatarioAviso


class AvisoUpdate(BaseModel):
    titulo: str | None = None
    mensagem: str | None = None
    destinatario_tipo: DestinatarioAviso | None = None


class AvisoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    evento_id: int
    titulo: str
    mensagem: str
    data_publicacao: datetime
    destinatario_tipo: DestinatarioAviso
