from fastapi import APIRouter, Depends

from models import Usuario
from dependencies import pegar_sessao
from main import bcrypt_context

auth_router = APIRouter(prefix='/auth', tags=['auth'])

@auth_router.get('/')
async def home():
    return {"msg":"rota padrão de autenticação"}

@auth_router.post("/criar-conta")
async def criar_conta(nome:str, email:str, senha:str, session=Depends(pegar_sessao)):
    usuario = session.query(Usuario).filter(Usuario.email == email).first()

    if usuario: # Já existe um usuário com esse email
        return {"msg":"já existe um usuário com esse email"}

    else: # Não existe um usuário com esse email
        senha_criptografada = bcrypt_context.hash(senha)
        novo_usuario = Usuario(nome, email, senha_criptografada)
        session.add(novo_usuario)
        session.commit()
        return {"msg":"usuário cadastrado com sucesso"}