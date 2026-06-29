from sqlalchemy.orm import Session

from app.core.exceptions import (
    CredenciaisInvalidasError,
    EmailJaCadastradoError,
    UsuarioNaoEncontradoError,
)
from app.core.security import create_access_token, hash_password, verify_password
from app.models.enums import TipoPerfil
from app.models.usuario import Usuario


def cadastrar_usuario(
    db: Session,
    nome: str,
    email: str,
    senha: str,
    tipo_perfil: TipoPerfil,
) -> Usuario:
    if db.query(Usuario).filter(Usuario.email == email).first():
        raise EmailJaCadastradoError()
    usuario = Usuario(
        nome=nome,
        email=email,
        senha_hash=hash_password(senha),
        tipo_perfil=tipo_perfil,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def autenticar_usuario(db: Session, email: str, senha: str) -> str:
    """Valida credenciais e retorna um JWT. Não distingue e-mail inexistente de senha errada."""
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario or not usuario.senha_hash or not verify_password(senha, usuario.senha_hash):
        raise CredenciaisInvalidasError()
    return create_access_token(
        subject=str(usuario.id),
        extra_claims={"perfil": usuario.tipo_perfil.value},
    )


def listar_cerimonialistas(db: Session) -> list[Usuario]:
    return (
        db.query(Usuario)
        .filter(Usuario.tipo_perfil == TipoPerfil.CERIMONIALISTA)
        .order_by(Usuario.nome)
        .all()
    )


def buscar_cerimonialista(db: Session, usuario_id: int) -> Usuario:
    usuario = (
        db.query(Usuario)
        .filter(Usuario.id == usuario_id, Usuario.tipo_perfil == TipoPerfil.CERIMONIALISTA)
        .first()
    )
    if usuario is None:
        raise UsuarioNaoEncontradoError()
    return usuario


def atualizar_usuario(
    db: Session,
    usuario: Usuario,
    nome: str | None = None,
    senha: str | None = None,
) -> Usuario:
    if nome is not None:
        usuario.nome = nome
    if senha is not None:
        usuario.senha_hash = hash_password(senha)
    db.commit()
    db.refresh(usuario)
    return usuario


def excluir_cerimonialista(db: Session, usuario_id: int) -> None:
    usuario = buscar_cerimonialista(db, usuario_id)
    db.delete(usuario)
    db.commit()
