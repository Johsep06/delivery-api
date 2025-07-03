from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordRequestForm

from models import Usuario
from dependencies import pegar_sessao, verificar_token
from main import bcrypt_context, ALGORITHM, SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES
from schemas import UsuarioSchemas, LoginSchemas

auth_router = APIRouter(prefix="/auth", tags=["auth"])

def criar_token(id_usuario:int, duracao_token:timedelta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    data_expiracao = datetime.now(timezone.utc) + duracao_token
    dic_info = {
        "sub":str(id_usuario),
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

@auth_router.post("/login")
async def login(login_schema:LoginSchemas, session:Session=Depends(pegar_sessao)):
    usuario = autenticar_usuario(login_schema.email, login_schema.senha, session)
    
    if not usuario:
        raise HTTPException(status_code=400, detail="Usuário não encontrado ou credenciais inválidas")
    else:
        access_token = criar_token(usuario.id)
        refresh_token = criar_token(usuario.id, duracao_token=timedelta(days=7))
        return {
            "access_token":access_token,
            "refresh_token":refresh_token,
            "token_type":"Bearer",
        }

@auth_router.post("/login-form")
async def login_form(data_form:OAuth2PasswordRequestForm=Depends(), session:Session=Depends(pegar_sessao)):
    usuario = autenticar_usuario(data_form.username, data_form.password, session)
    
    if not usuario:
        raise HTTPException(status_code=400, detail="Usuário não encontrado ou credenciais inválidas")
    else:
        access_token = criar_token(usuario.id)
        return {
            "access_token":access_token,
            "token_type":"Bearer",
        }

@auth_router.get("/refresh")
async def use_refresh_token(usuario:Usuario=Depends(verificar_token)):
    access_token = criar_token(usuario.id)
    return {
        "access_token":access_token,
        "token_type":"Bearer",
    }