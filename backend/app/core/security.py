"""
Funções utilitárias de segurança: hash/verificação de senha (bcrypt)
e criação/decodificação de tokens JWT.

Usado por: services de autenticação de Organizador e Cerimonialista.
Não se aplica ao acesso de Convidado, que usa token_confirmacao (ver app/core/tokens.py).
"""

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str, extra_claims: dict | None = None) -> str:
    """Gera um JWT. `subject` normalmente é o id do Usuario (organizador/cerimonialista)."""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    to_encode = {"sub": str(subject), "exp": expire}
    if extra_claims:
        to_encode.update(extra_claims)
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> dict | None:
    """Decodifica e valida o JWT. Retorna o payload ou None se inválido/expirado."""
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError:
        return None
