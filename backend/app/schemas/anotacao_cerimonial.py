from pydantic import BaseModel, ConfigDict, field_validator


class AnotacaoCerimonialCreate(BaseModel):
    momento_cerimonia: str
    descricao: str
    nomes_envolvidos: str | None = None
    ordem: int

    @field_validator("ordem")
    @classmethod
    def minimo_um(cls, v: int) -> int:
        if v < 1:
            raise ValueError("Deve ser >= 1")
        return v


class AnotacaoCerimonialUpdate(BaseModel):
    momento_cerimonia: str | None = None
    descricao: str | None = None
    nomes_envolvidos: str | None = None
    ordem: int | None = None

    @field_validator("ordem")
    @classmethod
    def minimo_um(cls, v: int | None) -> int | None:
        if v is not None and v < 1:
            raise ValueError("Deve ser >= 1")
        return v


class AnotacaoCerimonialRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    evento_id: int
    momento_cerimonia: str
    descricao: str
    nomes_envolvidos: str | None
    ordem: int
