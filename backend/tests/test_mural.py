"""
Testes do módulo de mural: álbuns, fotos, postagens, comentários e curtidas.
"""

from fastapi.testclient import TestClient

ORGANIZADOR = {"nome": "Ana Org", "email": "ana@mural.com", "senha": "senha123"}
ORGANIZADOR_B = {"nome": "Bruno Org", "email": "bruno@mural.com", "senha": "senha456"}
CERIMONIALISTA = {"nome": "Carlos Ceri", "email": "carlos@mural.com", "senha": "senha789"}

EVENTO_BASE = {
    "nome_debutante": "Júlia",
    "data_evento": "2025-06-15T20:00:00",
    "local": "Salão Estrelas",
    "max_acompanhantes_por_convidado": 2,
}

CONVIDADO_BASE = {
    "nome": "Pedro Convidado",
    "email": "pedro@mural.com",
    "telefone": "21999990001",
}

ALBUM_BASE = {"nome": "Making of"}
FOTO_BASE = {"url": "https://exemplo.com/foto1.jpg", "legenda": "Chegada da debutante"}
POSTAGEM_BASE = {"texto": "Que festa incrível!"}
COMENTARIO_BASE = {"texto": "Concordo plenamente!"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _cadastrar_e_login(client: TestClient, usuario: dict) -> str:
    client.post("/usuarios/organizador", json=usuario)
    resp = client.post(
        "/auth/login", data={"username": usuario["email"], "password": usuario["senha"]}
    )
    return resp.json()["access_token"]


def _token_cerimonialista(client: TestClient, token_org: str) -> str:
    client.post(
        "/usuarios/cerimonialista",
        json=CERIMONIALISTA,
        headers=_auth(token_org),
    )
    resp = client.post(
        "/auth/login",
        data={"username": CERIMONIALISTA["email"], "password": CERIMONIALISTA["senha"]},
    )
    return resp.json()["access_token"]


def _criar_evento(client: TestClient, token: str, payload: dict | None = None) -> dict:
    resp = client.post("/eventos", json=payload or EVENTO_BASE, headers=_auth(token))
    assert resp.status_code == 201
    return resp.json()


def _criar_convidado_e_login(
    client: TestClient, token_org: str, evento_id: int, payload: dict | None = None
) -> str:
    resp = client.post(
        f"/eventos/{evento_id}/convidados",
        json=payload or CONVIDADO_BASE,
        headers=_auth(token_org),
    )
    assert resp.status_code == 201
    token_confirmacao = resp.json()["token_confirmacao"]
    resp_login = client.post(
        "/auth/login/convidado", json={"token_confirmacao": token_confirmacao}
    )
    assert resp_login.status_code == 200
    return resp_login.json()["access_token"]


def _criar_album(
    client: TestClient, token: str, evento_id: int, payload: dict | None = None
) -> dict:
    resp = client.post(
        f"/eventos/{evento_id}/albuns", json=payload or ALBUM_BASE, headers=_auth(token)
    )
    assert resp.status_code == 201
    return resp.json()


def _criar_postagem(
    client: TestClient, token: str, evento_id: int, payload: dict | None = None
) -> dict:
    resp = client.post(
        f"/eventos/{evento_id}/postagens", json=payload or POSTAGEM_BASE, headers=_auth(token)
    )
    assert resp.status_code == 201
    return resp.json()


# ---------------------------------------------------------------------------
# Álbuns
# ---------------------------------------------------------------------------


def test_criar_album_por_organizador(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    resp = client.post(
        f"/eventos/{evento['id']}/albuns", json=ALBUM_BASE, headers=_auth(token)
    )
    assert resp.status_code == 201
    assert resp.json()["nome"] == ALBUM_BASE["nome"]
    assert resp.json()["fotos"] == []


def test_convidado_nao_cria_album_retorna_403(client):
    token_org = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token_org)
    token_conv = _criar_convidado_e_login(client, token_org, evento["id"])
    resp = client.post(
        f"/eventos/{evento['id']}/albuns", json=ALBUM_BASE, headers=_auth(token_conv)
    )
    assert resp.status_code == 403


def test_convidado_lista_albuns_do_proprio_evento(client):
    token_org = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token_org)
    _criar_album(client, token_org, evento["id"])
    token_conv = _criar_convidado_e_login(client, token_org, evento["id"])

    resp = client.get(f"/eventos/{evento['id']}/albuns", headers=_auth(token_conv))
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_convidado_nao_acessa_albuns_de_outro_evento_retorna_403(client):
    token_org = _cadastrar_e_login(client, ORGANIZADOR)
    evento_a = _criar_evento(client, token_org)
    evento_b = _criar_evento(client, token_org, {**EVENTO_BASE, "nome_debutante": "Laura"})
    token_conv_a = _criar_convidado_e_login(client, token_org, evento_a["id"])

    resp = client.get(f"/eventos/{evento_b['id']}/albuns", headers=_auth(token_conv_a))
    assert resp.status_code == 403


def test_atualizar_album(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    album = _criar_album(client, token, evento["id"])
    resp = client.patch(
        f"/eventos/{evento['id']}/albuns/{album['id']}",
        json={"nome": "Cerimônia"},
        headers=_auth(token),
    )
    assert resp.status_code == 200
    assert resp.json()["nome"] == "Cerimônia"


def test_excluir_album(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    album = _criar_album(client, token, evento["id"])
    resp = client.delete(f"/eventos/{evento['id']}/albuns/{album['id']}", headers=_auth(token))
    assert resp.status_code == 204
    resp_get = client.get(f"/eventos/{evento['id']}/albuns/{album['id']}", headers=_auth(token))
    assert resp_get.status_code == 404


# ---------------------------------------------------------------------------
# Fotos
# ---------------------------------------------------------------------------


def test_criar_foto_por_organizador(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    album = _criar_album(client, token, evento["id"])
    resp = client.post(
        f"/eventos/{evento['id']}/albuns/{album['id']}/fotos",
        json=FOTO_BASE,
        headers=_auth(token),
    )
    assert resp.status_code == 201
    assert resp.json()["url"] == FOTO_BASE["url"]
    assert resp.json()["legenda"] == FOTO_BASE["legenda"]


def test_convidado_lista_fotos(client):
    token_org = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token_org)
    album = _criar_album(client, token_org, evento["id"])
    client.post(
        f"/eventos/{evento['id']}/albuns/{album['id']}/fotos",
        json=FOTO_BASE,
        headers=_auth(token_org),
    )
    token_conv = _criar_convidado_e_login(client, token_org, evento["id"])

    resp = client.get(
        f"/eventos/{evento['id']}/albuns/{album['id']}/fotos", headers=_auth(token_conv)
    )
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_excluir_foto(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    album = _criar_album(client, token, evento["id"])
    foto = client.post(
        f"/eventos/{evento['id']}/albuns/{album['id']}/fotos",
        json=FOTO_BASE,
        headers=_auth(token),
    ).json()
    resp = client.delete(
        f"/eventos/{evento['id']}/albuns/{album['id']}/fotos/{foto['id']}", headers=_auth(token)
    )
    assert resp.status_code == 204


def test_foto_de_album_de_outro_evento_retorna_404(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento_a = _criar_evento(client, token)
    evento_b = _criar_evento(client, token, {**EVENTO_BASE, "nome_debutante": "Laura"})
    album_b = _criar_album(client, token, evento_b["id"])

    resp = client.post(
        f"/eventos/{evento_a['id']}/albuns/{album_b['id']}/fotos",
        json=FOTO_BASE,
        headers=_auth(token),
    )
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Postagens
# ---------------------------------------------------------------------------


def test_organizador_cria_postagem(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    resp = client.post(
        f"/eventos/{evento['id']}/postagens", json=POSTAGEM_BASE, headers=_auth(token)
    )
    assert resp.status_code == 201
    assert resp.json()["texto"] == POSTAGEM_BASE["texto"]
    assert resp.json()["comentarios"] == []
    assert resp.json()["curtidas"] == []


def test_convidado_cria_postagem(client):
    token_org = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token_org)
    token_conv = _criar_convidado_e_login(client, token_org, evento["id"])

    resp = client.post(
        f"/eventos/{evento['id']}/postagens", json=POSTAGEM_BASE, headers=_auth(token_conv)
    )
    assert resp.status_code == 201


def test_cerimonialista_cria_postagem(client):
    token_org = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token_org)
    token_ceri = _token_cerimonialista(client, token_org)

    resp = client.post(
        f"/eventos/{evento['id']}/postagens", json=POSTAGEM_BASE, headers=_auth(token_ceri)
    )
    assert resp.status_code == 201


def test_criar_postagem_sem_autenticacao_retorna_401(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    resp = client.post(f"/eventos/{evento['id']}/postagens", json=POSTAGEM_BASE)
    assert resp.status_code == 401


def test_listar_postagens_mais_recente_primeiro(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    _criar_postagem(client, token, evento["id"], {"texto": "Primeira"})
    _criar_postagem(client, token, evento["id"], {"texto": "Segunda"})

    resp = client.get(f"/eventos/{evento['id']}/postagens", headers=_auth(token))
    assert resp.status_code == 200
    textos = [p["texto"] for p in resp.json()]
    assert textos == ["Segunda", "Primeira"]


def test_convidado_exclui_propria_postagem(client):
    token_org = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token_org)
    token_conv = _criar_convidado_e_login(client, token_org, evento["id"])
    postagem = _criar_postagem(client, token_conv, evento["id"])

    resp = client.delete(
        f"/eventos/{evento['id']}/postagens/{postagem['id']}", headers=_auth(token_conv)
    )
    assert resp.status_code == 204


def test_organizador_exclui_postagem_de_convidado(client):
    token_org = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token_org)
    token_conv = _criar_convidado_e_login(client, token_org, evento["id"])
    postagem = _criar_postagem(client, token_conv, evento["id"])

    resp = client.delete(
        f"/eventos/{evento['id']}/postagens/{postagem['id']}", headers=_auth(token_org)
    )
    assert resp.status_code == 204


def test_convidado_nao_exclui_postagem_de_outro_retorna_403(client):
    token_org = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token_org)
    postagem = _criar_postagem(client, token_org, evento["id"])
    token_conv = _criar_convidado_e_login(client, token_org, evento["id"])

    resp = client.delete(
        f"/eventos/{evento['id']}/postagens/{postagem['id']}", headers=_auth(token_conv)
    )
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# Comentários
# ---------------------------------------------------------------------------


def test_convidado_comenta_postagem(client):
    token_org = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token_org)
    postagem = _criar_postagem(client, token_org, evento["id"])
    token_conv = _criar_convidado_e_login(client, token_org, evento["id"])

    resp = client.post(
        f"/eventos/{evento['id']}/postagens/{postagem['id']}/comentarios",
        json=COMENTARIO_BASE,
        headers=_auth(token_conv),
    )
    assert resp.status_code == 201
    assert resp.json()["texto"] == COMENTARIO_BASE["texto"]


def test_listar_comentarios(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    postagem = _criar_postagem(client, token, evento["id"])
    client.post(
        f"/eventos/{evento['id']}/postagens/{postagem['id']}/comentarios",
        json=COMENTARIO_BASE,
        headers=_auth(token),
    )

    resp = client.get(
        f"/eventos/{evento['id']}/postagens/{postagem['id']}/comentarios", headers=_auth(token)
    )
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_autor_exclui_proprio_comentario(client):
    token_org = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token_org)
    postagem = _criar_postagem(client, token_org, evento["id"])
    token_conv = _criar_convidado_e_login(client, token_org, evento["id"])
    comentario = client.post(
        f"/eventos/{evento['id']}/postagens/{postagem['id']}/comentarios",
        json=COMENTARIO_BASE,
        headers=_auth(token_conv),
    ).json()

    resp = client.delete(
        f"/eventos/{evento['id']}/postagens/{postagem['id']}/comentarios/{comentario['id']}",
        headers=_auth(token_conv),
    )
    assert resp.status_code == 204


def test_convidado_nao_exclui_comentario_de_outro_retorna_403(client):
    token_org = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token_org)
    postagem = _criar_postagem(client, token_org, evento["id"])
    comentario = client.post(
        f"/eventos/{evento['id']}/postagens/{postagem['id']}/comentarios",
        json=COMENTARIO_BASE,
        headers=_auth(token_org),
    ).json()
    token_conv = _criar_convidado_e_login(client, token_org, evento["id"])

    resp = client.delete(
        f"/eventos/{evento['id']}/postagens/{postagem['id']}/comentarios/{comentario['id']}",
        headers=_auth(token_conv),
    )
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# Curtidas
# ---------------------------------------------------------------------------


def test_convidado_curte_postagem(client):
    token_org = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token_org)
    postagem = _criar_postagem(client, token_org, evento["id"])
    token_conv = _criar_convidado_e_login(client, token_org, evento["id"])

    resp = client.post(
        f"/eventos/{evento['id']}/postagens/{postagem['id']}/curtir", headers=_auth(token_conv)
    )
    assert resp.status_code == 201

    resp_postagem = client.get(
        f"/eventos/{evento['id']}/postagens/{postagem['id']}", headers=_auth(token_conv)
    )
    assert len(resp_postagem.json()["curtidas"]) == 1


def test_curtir_duas_vezes_retorna_409(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    postagem = _criar_postagem(client, token, evento["id"])
    client.post(
        f"/eventos/{evento['id']}/postagens/{postagem['id']}/curtir", headers=_auth(token)
    )

    resp = client.post(
        f"/eventos/{evento['id']}/postagens/{postagem['id']}/curtir", headers=_auth(token)
    )
    assert resp.status_code == 409


def test_descurtir_postagem(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    postagem = _criar_postagem(client, token, evento["id"])
    client.post(
        f"/eventos/{evento['id']}/postagens/{postagem['id']}/curtir", headers=_auth(token)
    )

    resp = client.delete(
        f"/eventos/{evento['id']}/postagens/{postagem['id']}/curtir", headers=_auth(token)
    )
    assert resp.status_code == 204


def test_descurtir_sem_ter_curtido_retorna_404(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    postagem = _criar_postagem(client, token, evento["id"])

    resp = client.delete(
        f"/eventos/{evento['id']}/postagens/{postagem['id']}/curtir", headers=_auth(token)
    )
    assert resp.status_code == 404


def test_organizador_nao_acessa_postagens_de_outro_retorna_403(client):
    token_a = _cadastrar_e_login(client, ORGANIZADOR)
    token_b = _cadastrar_e_login(client, ORGANIZADOR_B)
    evento_b = _criar_evento(client, token_b)
    resp = client.get(f"/eventos/{evento_b['id']}/postagens", headers=_auth(token_a))
    assert resp.status_code == 403
