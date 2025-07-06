from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from dotenv import load_dotenv
import os

# Bloco de carrega de aariáveis de Ambiente
load_dotenv(override=True)
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

#  Inicialização do FastAPI
app = FastAPI()

# Criação de variável de criptografia
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Rota ppara login via formulario do framework
oauth2_schema = OAuth2PasswordBearer("auth/login-form")

# Importação das totas de autenticação e pedidos
from routes.auth_routes import auth_router
from routes.order_routes import order_router

# inclusão das totas no app
app.include_router(auth_router)
app.include_router(order_router)