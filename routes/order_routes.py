from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from schemas import PedidoSchemas
from dependencies import pegar_sessao   
from models import Pedidos

order_router = APIRouter(prefix="/order", tags=["order"])

@order_router.get("/")
async def orders():
    return {"msg":"Rota padrão de pedidos"}

@order_router.post("/pedido")
async def criar_pedido(pedido_schema:PedidoSchemas, session:Session=Depends(pegar_sessao)):
    novo_pedido = Pedidos(usuario=pedido_schema.usuario)
    session.add(novo_pedido)
    session.commit()

    return {"msg":"Pedido criado com sucesso"}