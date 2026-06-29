from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.usuario import TokenRead
from app.services.usuario_service import autenticar_usuario

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenRead)
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    token = autenticar_usuario(db, email=form.username, senha=form.password)
    return TokenRead(access_token=token)
