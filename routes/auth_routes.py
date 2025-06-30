from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from models import Usuario
from dependencies import pegar_sessao
from main import bcrypt_context
from schemas import UsuarioSchemas

auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.get("/")
async def home():
    return {"msg":"rota padrão de autenticação"}

@auth_router.post("/criar-conta")
async def criar_conta(usuario_schema:UsuarioSchemas, session:Session=Depends(pegar_sessao)):
    usuario = session.query(Usuario).filter(Usuario.email == usuario_schema.email).first()

    if usuario:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")

    else:
        senha_criptografada = bcrypt_context.hash(usuario_schema.senha)
        novo_usuario = Usuario(
            usuario_schema.nome,
            usuario_schema.email,
            senha_criptografada,
            usuario_schema.ativo,
            usuario_schema.admin
        )
        session.add(novo_usuario)
        session.commit()
        return {"msg":"usuário cadastrado com sucesso"}