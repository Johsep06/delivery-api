from sqlalchemy import create_engine, Column, String, Integer, Boolean, Float, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

# Inicializaçã do banco de dados
db = create_engine("sqlite:///banco.db")

# Declaração da Base para as classes virarem tabelas no Banco de dados
Base = declarative_base()

# Definição da classe\tabela de usuários
class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    nome = Column("nome", String)
    email = Column("email", String, nullable=False)
    senha = Column("senha", String)
    ativo = Column("ativo", Boolean)
    admin = Column("admin", Boolean, default=False)

    # Inicialização da classe para o "Insert", na tabela
    def __init__(self, nome:str, email:str, senha:str, ativo:bool=True, admin:bool=False) -> None:
        self.nome = nome
        self.email = email
        self.senha = senha
        self.ativo = ativo
        self.admin = admin
        
# Definição da classe\tabela de pedidos
class Pedido(Base):
    __tablename__ = "pedidos"
    
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    status = Column("status", String)
    usuario = Column("usuario", ForeignKey("usuarios.id"))
    preco = Column("preco", Float)
    itens = relationship("ItemPedido", cascade="all, delete")
    
    def __init__(self, usuario:int, status:str="PENDENTE", preco:float=0) -> None:
        self.usuario = usuario
        self.preco = preco
        self.status = status
        
    # Definição da função para calcular o preço do pedido
    def calcular_preco(self):
        self.preco = sum(item.quantidade * item.preco_unitario for item in self.itens)

# Definição da classe\tabela de itens do pedido
class ItemPedido(Base):
    __tablename__ = "itens_pedido"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    quantidade = Column("quantidade", Integer)
    sabor = Column("sabor", String)
    tamanho = Column("tamanho", String)
    preco_unitario = Column("preco_unitario", Float)
    pedido = Column("pedido", ForeignKey("pedidos.id"))
    
    def __init__(self, quantidade:int, sabor:str, tamanho:str, preco_unitario:float, pedido:int) -> None:
        self.quantidade = quantidade
        self.sabor = sabor
        self.tamanho = tamanho
        self.preco_unitario = preco_unitario
        self.pedido = pedido