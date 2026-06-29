from pydantic import BaseModel


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class RefreshResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LogoutRequest(BaseModel):
    refresh_token: str


class ConvidadoLoginRequest(BaseModel):
    token_confirmacao: str


class EsqueciSenhaRequest(BaseModel):
    email: str


class EsqueciSenhaResponse(BaseModel):
    mensagem: str
    # Em produção nunca expor o token — apenas para ambiente de desenvolvimento/testes.
    token_reset: str | None = None


class RedefinirSenhaRequest(BaseModel):
    token: str
    nova_senha: str


class AlterarSenhaRequest(BaseModel):
    senha_atual: str
    nova_senha: str
