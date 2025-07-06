from pydantic import BaseModel
from typing import Optional, List

# Arquivo para a definição dos schemas para facilitar a 
# valiação de dados de entrada, estruturar dados de saída e 
# Documentar a api automáticamente

class UsuarioSchemas(BaseModel):
    nome: str
    email: str
    senha: str
    ativo: Optional[bool]
    admin: Optional[bool]=False

    class Config:
        from_attributes = True

class PedidoSchemas(BaseModel):
    usuario: int

    class Config:
        from_attributes = True

class LoginSchemas(BaseModel):
    email:str
    senha:str
    
    class Config:
        from_attributes = True

class ItemPedidoSchema(BaseModel):
    quantidade:int
    sabor:str
    tamanho:str
    preco_unitario:float
    
    class Config:
        from_attributes = True
        
class ResponsePedidoSchema(BaseModel):
    id:int
    status:str
    preco:float
    itens: List[ItemPedidoSchema]
    
    class Config:
        from_attributes = True