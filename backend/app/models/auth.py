from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class RefreshToken(Base):
    """Token de renovação do JWT. Armazenado no banco para suportar revogação."""

    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    revogado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    data_expiracao: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    data_criacao: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    usuario = relationship("Usuario", back_populates="refresh_tokens")


class PasswordResetToken(Base):
    """Token de uso único para redefinição de senha. Expira em 15 minutos."""

    __tablename__ = "password_reset_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    usado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    data_expiracao: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    data_criacao: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    usuario = relationship("Usuario", back_populates="tokens_reset_senha")
