from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from schemas import PedidoSchemas, ItemPedidoSchema, ResponsePedidoSchema
from dependencies import pegar_sessao, verificar_token
from models import Pedido, Usuario, ItemPedido

# declara o prefixo da rota e garante que todas as rotas que vão herdar sejam pprotegidas por autenticação
order_router = APIRouter(prefix="/order", tags=["order"], dependencies=[Depends(verificar_token)])

@order_router.get("/")
async def orders():
    return {"msg":"Rota padrão de pedidos"}

@order_router.post("/pedido")
async def criar_pedido(pedido_schema:PedidoSchemas, session:Session=Depends(pegar_sessao)):
    """
    Cria um novo pedido no sistema.

    Returns:
        dict: mensagem de sucesso.
    """
    
    # Criar novo pedido com os dados do schema
    novo_pedido = Pedido(usuario=pedido_schema.usuario)
    # adiciona o pedido ao banco de dados
    session.add(novo_pedido)
    session.commit()

    return {"msg":"Pedido criado com sucesso"}

@order_router.post("/pedido/cancelar/{id_pedido}")
async def cancelar_pedido(id_pedido:int,
                          usuario:Usuario=Depends(verificar_token),
                          session:Session=Depends(pegar_sessao)
                          ):
    """
    Cancela um pedido no sistema.

    Args:
        id_pedido (int) : id do pedido a ser cancelado

    Returns:
        dict: mensagem de sucesso.
    """
    
    # recupera o pedido do banco de dados
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    # se não houver o pedido no banco de dados retornar um error
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não encontrado")
    # se o usuário não for admin ou dono do pedido o acesso a operação será negado
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=401, detail="Você não tem autorização para reaizar essa ação")
    
    # mudar o status do pedido
    pedido.status = "CANCELADO"
    session.commit()
    return {"msg":"Pedido Cancelado com sucesso"}

@order_router.get("/listar")
async def listar_pedidos(usuario:Usuario=Depends(verificar_token), session:Session=Depends(pegar_sessao)):
    """
    lista todos os pedidos salvos no banco de dados

    Returns:
        dict: list: pedidos
    """

    # se o usuário não for admin o acesso a operação será negado
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
    """
    Adiciona os itens ao pedido do sistema.

    Args:
        id_pedido (int) : id do pedido a ser adicionado o item
        item_pedido_schema (ItemPedidoSchema) : schema com os dados do item

    Returns:
        dict: mensagem de sucesso.
        int: id do item.
        int: preço do item
    """
    
    # recupera o pedido do banco de dados
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    
    # se o pedido não existir, cancelar a operação
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido Inexistente")
    # se o usuário não for admin e nem dono do pedido, cancelar a operação
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=401, detail="Você não tem autorização para reaizar essa ação")
    
    # cria o item com os dados no schema 
    item_pedido = ItemPedido(
        item_pedido_schema.quantidade,
        item_pedido_schema.sabor,
        item_pedido_schema.tamanho,
        item_pedido_schema.preco_unitario,
        id_pedido
    )
    
    # adiciona o item ao banco de dados
    session.add(item_pedido)

    # calcula o preço do pedido e adiciona ao banco
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
    """
    Remove um item do pedido.

    Args:
        id_item_pedido (int) : id do item pedido a ser removido do pedido

    Returns:
        dict: mensagem de sucesso.
    """
    
    # resgata o item do banco de dados 
    item_pedido = session.query(ItemPedido).filter(ItemPedido.id == id_item_pedido).first()
    # resgata um pedido do banco de dados
    pedido = session.query(Pedido).filter(Pedido.id == item_pedido.pedido).first()
    
    # se o item não existir no banco de dados, cancelar a operação
    if not item_pedido:
        raise HTTPException(status_code=400, detail="Item no Pedido Inexistente")
    # se o usuário não for admin e nem dono do pedido, cancelar a operação
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=401, detail="Você não tem autorização para reaizar essa ação")

    # deleta o item do banco de dados
    session.delete(item_pedido)
    # calcula o novo preço do pedido
    pedido.calcular_preco()
    # salva as alterações no banco de dados
    session.commit()
    return {
        "msg":"Item removido com sucesso",
    }

@order_router.post("/pedido/finalizar/{id_pedido}")
async def finalizar_pedido(id_pedido:int,
                           usuario:Usuario=Depends(verificar_token),
                           session:Session=Depends(pegar_sessao)
                            ):
    """
    Finaliza o status de um pedido.

    Args:
        id_pedido (int) : id do pedido a ser adicionado o item

    Returns:
        dict: mensagem de sucesso.
    """

    # resgata o pedido do banco de dados
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()

    # se o pedido não existir no banco de dados, cancelar a operação
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não encontrado")
    # se o usuário não for admin e nem dono do pedido, cancelar a operação
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=401, detail="Você não tem autorização para reaizar essa ação")
        
    # atualizar o status do pedido
    pedido.status = "FINALIZADO"
    # salva as alterações no banco de dados
    session.commit()
    return {"msg":"Pedido finalizado com sucesso"}

@order_router.get("/pedido/{id_pedido}")
async def vizualizar_pedido(id_pedido:int, 
                            usuario:Usuario=Depends(verificar_token),
                            session:Session=Depends(pegar_sessao)
                            ):
    """
    Exibe um item do pedido.

    Args:
        id_pedido (int) : id do pedido a ser adicionado o item

    Returns:
        int: quantidade de itens no pedido.
        Pedido: dados do pedido.
    """
    
    
    # resgata o pedido do banco de dados
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    # se o pedido não existir no banco de dados, cancelar a operação
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não encontrado")
    # se o usuário não for admin e nem dono do pedido, cancelar a operação
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=401, detail="Você não tem autorização para reaizar essa ação")

    return {
        "quantidade_itens_pedido":len(pedido.itens),
        "pedido":pedido
    }

@order_router.get("/listar/pedidos-usuario", response_model=List[ResponsePedidoSchema])
async def listar_pedidos(usuario:Usuario=Depends(verificar_token), session:Session=Depends(pegar_sessao)):
    """
    Exibe todos os pedidos do usuário

    Returns:
        list: lista de todos os pedidos formatados por um schema.
    """
    pedidos = session.query(Pedido).filter(Pedido.usuario == usuario.id).all()
    return pedidos