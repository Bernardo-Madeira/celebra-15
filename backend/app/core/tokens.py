"""
Geração do token_confirmacao usado no link individual de confirmação de
presença do Convidado (acesso sem login — ver RNF02 no Cap. 4 do TCC).
"""

import secrets


def gerar_token_confirmacao(n_bytes: int = 32) -> str:
    """Gera um token único, não previsível, seguro para uso em URL (urlsafe)."""
    return secrets.token_urlsafe(n_bytes)
