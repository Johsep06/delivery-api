from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from schemas import PedidoSchemas, ItemPedidoSchema
from dependencies import pegar_sessao, verificar_token
from models import Pedido, Usuario, ItemPedido

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
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não encontrado")
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=401, detail="Você não tem autorização para reaizar essa ação")
        
    pedido.status = "CANCELADO"
    session.commit()
    return {"msg":"Pedido Cancelado com sucesso"}

@order_router.get("/listar")
async def listar_pedidos(usuario:Usuario=Depends(verificar_token), session:Session=Depends(pegar_sessao)):
    if not usuario.admin:
        raise HTTPException(status_code=401, detail="Você não tem autorização para realizar essa ação")
    else:
        pedidos = session.query(Pedido).all()
        return {
            "pedidos":pedidos
        }

@order_router.post("/pedidos/adicionar-item/{id_pedido}")
async def adicionar_item_pedido(id_pedido:int,
                                item_pedido_schema:ItemPedidoSchema,
                                usuario:Usuario=Depends(verificar_token), 
                                session:Session=Depends(pegar_sessao)
                                ):
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido Inexistente")
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=401, detail="Você não tem autorização para reaizar essa ação")
    item_pedido = ItemPedido(
        item_pedido_schema.quantidade,
        item_pedido_schema.sabor,
        item_pedido_schema.tamanho,
        item_pedido_schema.preco_unitario,
        id_pedido
    )
    session.add(item_pedido)
    pedido.calcular_preco()
    session.commit()
    return {
        "msg":"Item adicionado ao pedido com sucesso",
        "item_id":item_pedido.id,
        "preco_pedido":pedido.preco,

    }
    
@order_router.post("/pedidos/remover-item/{id_item_pedido}")
async def remover_item_pedido(id_item_pedido:int,
                                usuario:Usuario=Depends(verificar_token), 
                                session:Session=Depends(pegar_sessao)
                                ):
    item_pedido = session.query(ItemPedido).filter(ItemPedido.id == id_item_pedido).first()
    pedido = session.query(Pedido).filter(Pedido.id == item_pedido.pedido).first()
    
    if not item_pedido:
        raise HTTPException(status_code=400, detail="Item no Pedido Inexistente")
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=401, detail="Você não tem autorização para reaizar essa ação")
    session.delete(item_pedido)
    pedido.calcular_preco()
    session.commit()
    return {
        "msg":"Item removido com sucesso",
    }

@order_router.post("/pedido/finalizar/{id_pedido}")
async def finalizar_pedido(id_pedido:int,
                           usuario:Usuario=Depends(verificar_token),
                           session:Session=Depends(pegar_sessao)
                            ):
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não encontrado")
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=401, detail="Você não tem autorização para reaizar essa ação")
        
    pedido.status = "FINALIZADO"
    session.commit()
    return {"msg":"Pedido finalizado com sucesso"}

@order_router.get("/pedido/{id_pedido}")
async def vizualizar_pedido(id_pedido:int, 
                            usuario:Usuario=Depends(verificar_token),
                            session:Session=Depends(pegar_sessao)
                            ):
    
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não encontrado")
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=401, detail="Você não tem autorização para reaizar essa ação")

    return {
        "quantidade_itens_pedido":len(pedido.itens),
        "pedido":pedido
    }