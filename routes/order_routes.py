from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from schemas import PedidoSchemas
from dependencies import pegar_sessao, verificar_token
from models import Pedido, Usuario

order_router = APIRouter(prefix="/order", tags=["order"], dependencies=[Depends(verificar_token)])

@order_router.get("/")
async def orders():
    return {"msg":"Rota padrão de pedidos"}

@order_router.post("/pedido")
async def criar_pedido(pedido_schema:PedidoSchemas, session:Session=Depends(pegar_sessao)):
    novo_pedido = Pedido(usuario=pedido_schema.usuario)
    session.add(novo_pedido)
    session.commit()

    return {"msg":"Pedido criado com sucesso"}

@order_router.post("/pedido/cancelar/{id_pedido}")
async def cancelar_pedido(id_pedido:int, usuario:Usuario=Depends(verificar_token), session:Session=Depends(pegar_sessao)):
    pedido = session.query(Pedido).filter(Pedido.id==id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não encontrado")
    if not usuario.admin or usuario.id != pedido.id:
        raise HTTPException(status_code=401, detail="Você não tem autorização para reaizar essa ação")
        
    pedido.status = "CANCELADO"
    session.commit()
    return {"msg":"Pedido Cancelado com sucesso"}