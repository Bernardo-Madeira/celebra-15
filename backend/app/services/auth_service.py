"""
Lógica de negócio de autenticação:
  - login (credenciais → access_token + refresh_token)
  - renovação de token (refresh)
  - logout (revogação de refresh token)
  - login de convidado (token_confirmacao → access_token + refresh_token)
  - recuperação de senha (esqueci-senha / redefinir-senha)
  - alteração de senha autenticada
"""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import (
    ConvidadoNaoEncontradoError,
    CredenciaisInvalidasError,
    SenhaAtualInvalidaError,
    TokenExpiradoError,
    TokenInvalidoError,
)
from app.core.security import (
    create_access_token,
    generate_password_reset_token,
    generate_refresh_token,
    hash_password,
    verify_password,
)
from app.models.auth import PasswordResetToken, RefreshToken
from app.models.convidado import Convidado
from app.models.usuario import Usuario


def _criar_par_tokens(db: Session, usuario: Usuario) -> tuple[str, str]:
    """Cria e persiste um novo par access_token / refresh_token para o usuário."""
    access_token = create_access_token(
        subject=str(usuario.id),
        extra_claims={"perfil": usuario.tipo_perfil.value},
    )
    raw_refresh, expires_at = generate_refresh_token()
    refresh_token_record = RefreshToken(
        usuario_id=usuario.id,
        token=raw_refresh,
        data_expiracao=expires_at,
    )
    db.add(refresh_token_record)
    db.commit()
    return access_token, raw_refresh


def login(db: Session, email: str, senha: str) -> tuple[str, str]:
    """Valida credenciais e retorna (access_token, refresh_token)."""
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario or not usuario.senha_hash or not verify_password(senha, usuario.senha_hash):
        raise CredenciaisInvalidasError()
    return _criar_par_tokens(db, usuario)


def renovar_token(db: Session, refresh_token_raw: str) -> tuple[str, str]:
    """Valida o refresh token, revoga-o e emite um novo par (rotação)."""
    record = (
        db.query(RefreshToken)
        .filter(RefreshToken.token == refresh_token_raw, RefreshToken.revogado.is_(False))
        .first()
    )
    if record is None:
        raise TokenInvalidoError()

    agora = datetime.now(timezone.utc)
    expiracao = record.data_expiracao
    if expiracao.tzinfo is None:
        from datetime import timezone as tz
        expiracao = expiracao.replace(tzinfo=tz.utc)

    if expiracao < agora:
        raise TokenExpiradoError()

    # Rotação: revoga o token atual antes de emitir o novo
    record.revogado = True
    db.flush()

    return _criar_par_tokens(db, record.usuario)


def logout(db: Session, refresh_token_raw: str) -> None:
    """Revoga o refresh token informado."""
    record = (
        db.query(RefreshToken)
        .filter(RefreshToken.token == refresh_token_raw, RefreshToken.revogado.is_(False))
        .first()
    )
    if record is None:
        raise TokenInvalidoError()
    record.revogado = True
    db.commit()


def login_convidado(db: Session, token_confirmacao: str) -> tuple[str, str]:
    """Autentica um convidado pelo token_confirmacao e retorna o par de tokens."""
    convidado = (
        db.query(Convidado)
        .filter(Convidado.token_confirmacao == token_confirmacao)
        .first()
    )
    if convidado is None:
        raise ConvidadoNaoEncontradoError()
    return _criar_par_tokens(db, convidado.usuario)


def solicitar_reset_senha(db: Session, email: str) -> str:
    """
    Gera um token de reset de senha para o e-mail informado.
    Retorna o token (para envio por e-mail em produção).
    Nunca revela se o e-mail existe ou não ao chamador via exceção.
    """
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario or not usuario.senha_hash:
        # Retorna string vazia — o router sempre responde 200 para não enumerar usuários
        return ""

    raw_token, expires_at = generate_password_reset_token()
    db.add(PasswordResetToken(
        usuario_id=usuario.id,
        token=raw_token,
        data_expiracao=expires_at,
    ))
    db.commit()
    return raw_token


def redefinir_senha(db: Session, token_raw: str, nova_senha: str) -> None:
    """Valida o token de reset e aplica a nova senha."""
    record = (
        db.query(PasswordResetToken)
        .filter(PasswordResetToken.token == token_raw, PasswordResetToken.usado.is_(False))
        .first()
    )
    if record is None:
        raise TokenInvalidoError()

    agora = datetime.now(timezone.utc)
    expiracao = record.data_expiracao
    if expiracao.tzinfo is None:
        expiracao = expiracao.replace(tzinfo=timezone.utc)

    if expiracao < agora:
        raise TokenExpiradoError()

    record.usado = True
    record.usuario.senha_hash = hash_password(nova_senha)

    # Revoga todos os refresh tokens do usuário para forçar novo login
    db.query(RefreshToken).filter(
        RefreshToken.usuario_id == record.usuario_id,
        RefreshToken.revogado.is_(False),
    ).update({"revogado": True})

    db.commit()


def alterar_senha(db: Session, usuario: Usuario, senha_atual: str, nova_senha: str) -> None:
    """Troca a senha do usuário autenticado após verificar a senha atual."""
    if not usuario.senha_hash or not verify_password(senha_atual, usuario.senha_hash):
        raise SenhaAtualInvalidaError()

    usuario.senha_hash = hash_password(nova_senha)

    # Revoga todos os refresh tokens para forçar novo login em outros dispositivos
    db.query(RefreshToken).filter(
        RefreshToken.usuario_id == usuario.id,
        RefreshToken.revogado.is_(False),
    ).update({"revogado": True})

    db.commit()
