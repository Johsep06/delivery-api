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
    """
    Cria um token para o usuário manter a conexão.

    Args:
        id_usuario (int) : id do usuário
        duracao_token (int) : tempo de duração do token
    Returns:
        str: token de conexão do usuário
    """
    
    # cálcula o tempo de duração do token
    data_expiracao = datetime.now(timezone.utc) + duracao_token
    # gera o token com as infos do usuário
    dic_info = {
        "sub":str(id_usuario),
        "exp":data_expiracao
    }
    
    # gera o token do usuário com a chave secreta do sistema e o algorítimo para a criptografia
    jwt_codifiado = jwt.encode(dic_info, SECRET_KEY, ALGORITHM)
    
    return jwt_codifiado

def autenticar_usuario(email:str, senha:str, session:Session):
    """
    Autentica o usuário.

    Args:
        email (str) : email do usuário.
        senha (str) : senha do usuário
        session (Session) : Sessão do banco de dados

    Returns:
        usuario : objeto usuário
    """
    
    # resgata o usuário do banco de dados pelo email.
    usuario = session.query(Usuario).filter(Usuario.email == email).first()

    # se o usuário não exixtir, cancelar a operação
    if not usuario:
        return False
    # se a senha não for a mesma salva no sistema, cancelar a operação
    elif not bcrypt_context.verify(senha, usuario.senha):
        return False

    return usuario

@auth_router.get("/")
async def home():
    """
    Rota padrão de autenticação

    Returns:
        dict: mensagem de sucesso.
    """
    return {"msg":"rota padrão de autenticação"}

@auth_router.post("/criar-conta")
async def criar_conta(usuario_schema:UsuarioSchemas, session:Session=Depends(pegar_sessao)):
    """
    Cria uma nova conta no sistema

    Args:
        usuario_schema (UsuarioSchemas) : schema com os dados do usuário

    Returns:
        dict: mensagem de sucesso.
    """
    # tenta resgatar um usuário do sistema pelo email
    usuario = session.query(Usuario).filter(Usuario.email == usuario_schema.email).first()

    if usuario: # se já existir um usuário no sistema com o email, cancelar a operação
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")

    else: # se mão exitir um usuário com o email, prosseguir para o cadastro
        # criptografa a senha
        senha_criptografada = bcrypt_context.hash(usuario_schema.senha)
        # cria o objeto usuário
        novo_usuario = Usuario(
            usuario_schema.nome,
            usuario_schema.email,
            senha_criptografada,
            usuario_schema.ativo,
            usuario_schema.admin
        )
        # adiciona o usuário ao sistema 
        session.add(novo_usuario)
        # e salva as alterações do banco de dados
        session.commit()
        return {"msg":"usuário cadastrado com sucesso"}

@auth_router.post("/login")
async def login(login_schema:LoginSchemas, session:Session=Depends(pegar_sessao)):
    """
    Faz o login do usuário.

    Args:
        login_schema (LoginSchema) : schema com os dados para o login

    Returns:
        dict: tokens para acesso, tipo de token.
    """
    # autentica o usuário
    usuario = autenticar_usuario(login_schema.email, login_schema.senha, session)
    
    # se o usuário não existir ou os dados forem inválidos, cancelar a operação
    if not usuario:
        raise HTTPException(status_code=400, detail="Usuário não encontrado ou credenciais inválidas")
    else:
        # gera um token de duração curta e outro mais longo
        access_token = criar_token(usuario.id)
        refresh_token = criar_token(usuario.id, duracao_token=timedelta(days=7))
        return {
            "access_token":access_token,
            "refresh_token":refresh_token,
            "token_type":"Bearer",
        }

@auth_router.post("/login-form")
async def login_form(data_form:OAuth2PasswordRequestForm=Depends(), session:Session=Depends(pegar_sessao)):
    """
    Faz o login do usuário vila formulário da documentação da API.

    Returns:
        dict: tokens para acesso, tipo de token.
    """
    
    # autentica o usuário
    usuario = autenticar_usuario(data_form.username, data_form.password, session)
    
    # se o usuário não existir ou os dados forem inválidos, cancelar a operação
    if not usuario:
        raise HTTPException(status_code=400, detail="Usuário não encontrado ou credenciais inválidas")
    else:
        # gera um token de duração curta
        access_token = criar_token(usuario.id)
        return {
            "access_token":access_token,
            "token_type":"Bearer",
        }

@auth_router.get("/refresh")
async def use_refresh_token(usuario:Usuario=Depends(verificar_token)):
    """
    Gera um novo access token com base no refres_token.

    Returns:
        dict: access token e tipo de token.
    """
    access_token = criar_token(usuario.id)
    return {
        "access_token":access_token,
        "token_type":"Bearer",
    }