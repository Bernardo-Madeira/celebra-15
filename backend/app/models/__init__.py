"""
Centraliza o import de todos os models para que fiquem registrados em
Base.metadata antes do Alembic autogenerate (ver backend/alembic/env.py,
que importa `app.models`).
"""

from app.models.usuario import Usuario
from app.models.auth import RefreshToken, PasswordResetToken
from app.models.evento import Evento
from app.models.convidado import Convidado, Acompanhante, Mesa
from app.models.presente import Presente, ReservaPresente
from app.models.fornecedor import Fornecedor, Pagamento
from app.models.tarefa import Tarefa
from app.models.cerimonial import Homenagem, AnotacaoCerimonial
from app.models.playlist import Musica, SugestaoMusical, VotoMusica
from app.models.aviso import Aviso
from app.models.mural import Album, Foto, Postagem, Comentario, Curtida

__all__ = [
    "Usuario",
    "RefreshToken",
    "PasswordResetToken",
    "Evento",
    "Convidado",
    "Acompanhante",
    "Mesa",
    "Presente",
    "ReservaPresente",
    "Fornecedor",
    "Pagamento",
    "Tarefa",
    "Homenagem",
    "AnotacaoCerimonial",
    "Musica",
    "SugestaoMusical",
    "VotoMusica",
    "Aviso",
    "Album",
    "Foto",
    "Postagem",
    "Comentario",
    "Curtida",
]
