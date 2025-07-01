from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone

from models import Usuario
from dependencies import pegar_sessao
from main import bcrypt_context, ALGORITHM, SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES
from schemas import UsuarioSchemas, LoginSchemas

auth_router = APIRouter(prefix="/auth", tags=["auth"])

def criar_token(id_usuario:int):
    data_expiracao = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    dic_info = {
        "sub":id_usuario,
        "exp":data_expiracao
    }
    jwt_codifiado = jwt.encode(dic_info, SECRET_KEY, ALGORITHM)
    
    return jwt_codifiado

def autenticar_usuario(email:str, senha:str, session:Session):
    usuario = session.query(Usuario).filter(Usuario.email == email).first()

    if not usuario:
        return False
    elif not bcrypt_context.verify(senha, usuario.senha):
        return False

    return usuario

@auth_router.get("/")
async def home():
    return {"msg":"rota padrão de autenticação"}

@auth_router.post("/criar-conta")
async def criar_conta(usuario_schema:UsuarioSchemas, session:Session=Depends(pegar_sessao)):
    usuario = session.query(Usuario).filter(Usuario.email == usuario_schema.email).first()

    if usuario: # Já existe um usuário com esse email
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")

    else: # Não existe um usuário com esse email
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

@auth_router.post("/")
async def login(login_schema:LoginSchemas, session:Session=Depends(pegar_sessao)):
    usuario = autenticar_usuario(login_schema.email, login_schema.senha, session)
    
    if not usuario:
        raise HTTPException(status_code=400, detail="Usuário não encontrado ou credenciais inválidas")
    else:
        access_token = criar_token(usuario.id)
        return {
            "access_token":access_token,
            "token_type":"Bearer",
        }