from pydantic import BaseModel, ConfigDict, field_validator


class HomenagemCreate(BaseModel):
    homenageado: str
    texto: str
    ordem: int
    autor: str | None = None

    @field_validator("ordem")
    @classmethod
    def minimo_um(cls, v: int) -> int:
        if v < 1:
            raise ValueError("Deve ser >= 1")
        return v


class HomenagemUpdate(BaseModel):
    homenageado: str | None = None
    texto: str | None = None
    ordem: int | None = None
    autor: str | None = None

    @field_validator("ordem")
    @classmethod
    def minimo_um(cls, v: int | None) -> int | None:
        if v is not None and v < 1:
            raise ValueError("Deve ser >= 1")
        return v


class HomenagemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    evento_id: int
    homenageado: str
    texto: str
    ordem: int
    autor: str | None
