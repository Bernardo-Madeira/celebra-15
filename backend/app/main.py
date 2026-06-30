from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.core.exceptions import (
    AcessoNegadoError,
    AnotacaoCerimonialNaoEncontradaError,
    ConvidadoNaoEncontradoError,
    CotaPresenteEsgotadaError,
    CredenciaisInvalidasError,
    EmailJaCadastradoError,
    EventoNaoEncontradoError,
    FornecedorNaoEncontradoError,
    HomenagemNaoEncontradaError,
    LimiteAcompanhantesExcedidoError,
    MesaLotadaError,
    MesaNaoEncontradaError,
    PagamentoNaoEncontradoError,
    PresenteNaoEncontradoError,
    ReservaPresenteJaExisteError,
    ReservaPresenteNaoEncontradaError,
    SenhaAtualInvalidaError,
    TarefaNaoEncontradoError,
    TokenExpiradoError,
    TokenInvalidoError,
    TokenJaUsadoError,
    UsuarioNaoEncontradoError,
    ValorSinalInvalidoError,
)
from app.routers import auth, health, usuario
from app.routers.anotacao_cerimonial import router as anotacao_cerimonial_router
from app.routers.convidado import confirmacao_router, router as convidado_router
from app.routers.evento import router as evento_router
from app.routers.fornecedor import router as fornecedor_router
from app.routers.homenagem import router as homenagem_router
from app.routers.presente import reserva_router as presente_reserva_router, router as presente_router
from app.routers.tarefa import router as tarefa_router

app = FastAPI(
    title="celebra-15 API",
    description="API do Sistema de Gestão de Eventos de Debutantes (TCC FAETERJ).",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(EmailJaCadastradoError)
async def email_ja_cadastrado_handler(request: Request, exc: EmailJaCadastradoError):
    return JSONResponse(status_code=409, content={"detail": "E-mail já cadastrado."})


@app.exception_handler(CredenciaisInvalidasError)
async def credenciais_invalidas_handler(request: Request, exc: CredenciaisInvalidasError):
    return JSONResponse(status_code=401, content={"detail": "Credenciais inválidas."})


@app.exception_handler(UsuarioNaoEncontradoError)
async def usuario_nao_encontrado_handler(request: Request, exc: UsuarioNaoEncontradoError):
    return JSONResponse(status_code=404, content={"detail": "Usuário não encontrado."})


@app.exception_handler(TokenInvalidoError)
async def token_invalido_handler(request: Request, exc: TokenInvalidoError):
    return JSONResponse(status_code=401, content={"detail": "Token inválido ou revogado."})


@app.exception_handler(TokenExpiradoError)
async def token_expirado_handler(request: Request, exc: TokenExpiradoError):
    return JSONResponse(status_code=401, content={"detail": "Token expirado."})


@app.exception_handler(TokenJaUsadoError)
async def token_ja_usado_handler(request: Request, exc: TokenJaUsadoError):
    return JSONResponse(status_code=400, content={"detail": "Token já foi utilizado."})


@app.exception_handler(SenhaAtualInvalidaError)
async def senha_atual_invalida_handler(request: Request, exc: SenhaAtualInvalidaError):
    return JSONResponse(status_code=400, content={"detail": "Senha atual incorreta."})


@app.exception_handler(ConvidadoNaoEncontradoError)
async def convidado_nao_encontrado_handler(request: Request, exc: ConvidadoNaoEncontradoError):
    return JSONResponse(status_code=404, content={"detail": "Convidado não encontrado."})


@app.exception_handler(EventoNaoEncontradoError)
async def evento_nao_encontrado_handler(request: Request, exc: EventoNaoEncontradoError):
    return JSONResponse(status_code=404, content={"detail": "Evento não encontrado."})


@app.exception_handler(AcessoNegadoError)
async def acesso_negado_handler(request: Request, exc: AcessoNegadoError):
    return JSONResponse(status_code=403, content={"detail": "Acesso negado."})


@app.exception_handler(MesaNaoEncontradaError)
async def mesa_nao_encontrada_handler(request: Request, exc: MesaNaoEncontradaError):
    return JSONResponse(status_code=404, content={"detail": "Mesa não encontrada."})


@app.exception_handler(MesaLotadaError)
async def mesa_lotada_handler(request: Request, exc: MesaLotadaError):
    return JSONResponse(status_code=422, content={"detail": "Mesa sem capacidade disponível."})


@app.exception_handler(LimiteAcompanhantesExcedidoError)
async def limite_acompanhantes_handler(request: Request, exc: LimiteAcompanhantesExcedidoError):
    return JSONResponse(
        status_code=422, content={"detail": "Número máximo de acompanhantes excedido."}
    )


@app.exception_handler(PresenteNaoEncontradoError)
async def presente_nao_encontrado_handler(request: Request, exc: PresenteNaoEncontradoError):
    return JSONResponse(status_code=404, content={"detail": "Presente não encontrado."})


@app.exception_handler(ReservaPresenteNaoEncontradaError)
async def reserva_presente_nao_encontrada_handler(
    request: Request, exc: ReservaPresenteNaoEncontradaError
):
    return JSONResponse(status_code=404, content={"detail": "Reserva não encontrada."})


@app.exception_handler(ReservaPresenteJaExisteError)
async def reserva_presente_ja_existe_handler(request: Request, exc: ReservaPresenteJaExisteError):
    return JSONResponse(
        status_code=409, content={"detail": "Você já contribuiu com este presente."}
    )


@app.exception_handler(CotaPresenteEsgotadaError)
async def cota_presente_esgotada_handler(request: Request, exc: CotaPresenteEsgotadaError):
    return JSONResponse(
        status_code=422, content={"detail": "Cota de contribuintes deste presente esgotada."}
    )


@app.exception_handler(FornecedorNaoEncontradoError)
async def fornecedor_nao_encontrado_handler(request: Request, exc: FornecedorNaoEncontradoError):
    return JSONResponse(status_code=404, content={"detail": "Fornecedor não encontrado."})


@app.exception_handler(PagamentoNaoEncontradoError)
async def pagamento_nao_encontrado_handler(request: Request, exc: PagamentoNaoEncontradoError):
    return JSONResponse(status_code=404, content={"detail": "Pagamento não encontrado."})


@app.exception_handler(ValorSinalInvalidoError)
async def valor_sinal_invalido_handler(request: Request, exc: ValorSinalInvalidoError):
    return JSONResponse(
        status_code=422, content={"detail": "Valor do sinal não pode ser maior que o valor total."}
    )


@app.exception_handler(TarefaNaoEncontradoError)
async def tarefa_nao_encontrado_handler(request: Request, exc: TarefaNaoEncontradoError):
    return JSONResponse(status_code=404, content={"detail": "Tarefa não encontrada."})


@app.exception_handler(HomenagemNaoEncontradaError)
async def homenagem_nao_encontrada_handler(request: Request, exc: HomenagemNaoEncontradaError):
    return JSONResponse(status_code=404, content={"detail": "Homenagem não encontrada."})


@app.exception_handler(AnotacaoCerimonialNaoEncontradaError)
async def anotacao_cerimonial_nao_encontrada_handler(
    request: Request, exc: AnotacaoCerimonialNaoEncontradaError
):
    return JSONResponse(status_code=404, content={"detail": "Anotação cerimonial não encontrada."})


app.include_router(health.router)
app.include_router(auth.router)
app.include_router(usuario.router)
app.include_router(evento_router)
app.include_router(convidado_router)
app.include_router(confirmacao_router)
app.include_router(presente_router)
app.include_router(presente_reserva_router)
app.include_router(fornecedor_router)
app.include_router(tarefa_router)
app.include_router(homenagem_router)
app.include_router(anotacao_cerimonial_router)

# Próximos routers a registrar aqui conforme implementados:
# musicas, avisos, albuns, fotos, postagens, comentarios, curtidas


@app.get("/")
def root():
    return {"message": "celebra-15 API — ver /docs para a documentação interativa."}
