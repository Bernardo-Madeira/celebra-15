from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.database import get_db
from app.models.enums import TipoPerfil
from app.models.usuario import Usuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_usuario(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    usuario = db.get(Usuario, int(payload["sub"]))
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return usuario


def require_organizador(
    usuario: Usuario = Depends(get_current_usuario),
) -> Usuario:
    if usuario.tipo_perfil != TipoPerfil.ORGANIZADOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas organizadores podem realizar esta ação.",
        )
    return usuario


def require_organizador_ou_cerimonialista(
    usuario: Usuario = Depends(get_current_usuario),
) -> Usuario:
    if usuario.tipo_perfil not in (TipoPerfil.ORGANIZADOR, TipoPerfil.CERIMONIALISTA):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a organizadores e cerimonialistas.",
        )
    return usuario
