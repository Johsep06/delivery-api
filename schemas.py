from pydantic import BaseModel
from typing import Optional

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