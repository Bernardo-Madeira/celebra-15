from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.deps import get_current_usuario
from app.db.database import get_db
from app.models.usuario import Usuario
from app.schemas.auth import (
    AlterarSenhaRequest,
    ConvidadoLoginRequest,
    EsqueciSenhaRequest,
    EsqueciSenhaResponse,
    LoginResponse,
    LogoutRequest,
    RedefinirSenhaRequest,
    RefreshRequest,
    RefreshResponse,
)
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Login com e-mail e senha. Retorna access_token (curta duração) e refresh_token (7 dias)."""
    access_token, refresh_token = auth_service.login(db, email=form.username, senha=form.password)
    return LoginResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=RefreshResponse)
def refresh(
    body: RefreshRequest,
    db: Session = Depends(get_db),
):
    """
    Renova o access_token usando um refresh_token válido.
    O refresh_token atual é revogado e um novo par é emitido (rotação de token).
    """
    access_token, new_refresh = auth_service.renovar_token(db, body.refresh_token)
    return RefreshResponse(access_token=access_token, refresh_token=new_refresh)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    body: LogoutRequest,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_usuario),
):
    """Revoga o refresh_token informado. O access_token expira naturalmente."""
    auth_service.logout(db, body.refresh_token)


@router.post("/login/convidado", response_model=LoginResponse)
def login_convidado(
    body: ConvidadoLoginRequest,
    db: Session = Depends(get_db),
):
    """Autentica um convidado usando seu token_confirmacao único (sem senha)."""
    access_token, refresh_token = auth_service.login_convidado(db, body.token_confirmacao)
    return LoginResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/esqueci-senha", response_model=EsqueciSenhaResponse)
def esqueci_senha(
    body: EsqueciSenhaRequest,
    db: Session = Depends(get_db),
):
    """
    Solicita redefinição de senha. Sempre retorna 200 para não revelar
    quais e-mails estão cadastrados. Em produção o token seria enviado por e-mail;
    aqui é retornado na resposta para facilitar testes.
    """
    token = auth_service.solicitar_reset_senha(db, body.email)
    return EsqueciSenhaResponse(
        mensagem="Se o e-mail estiver cadastrado, um link de redefinição foi enviado.",
        token_reset=token if token else None,
    )


@router.post("/redefinir-senha", status_code=status.HTTP_204_NO_CONTENT)
def redefinir_senha(
    body: RedefinirSenhaRequest,
    db: Session = Depends(get_db),
):
    """Redefine a senha usando um token de reset válido (uso único, 15 minutos)."""
    auth_service.redefinir_senha(db, body.token, body.nova_senha)


@router.post("/alterar-senha", status_code=status.HTTP_204_NO_CONTENT)
def alterar_senha(
    body: AlterarSenhaRequest,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_usuario),
):
    """Altera a senha do usuário autenticado. Exige a senha atual e revoga todos os refresh tokens."""
    auth_service.alterar_senha(db, usuario, body.senha_atual, body.nova_senha)
