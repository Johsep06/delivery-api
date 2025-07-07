# Delivery API

<strong>Delivery API</strong> é um protótipo de backend para gerenciamento de pedidos de entrega, implementado em Python com FastAPI. O objetivo é demonstrar boas práticas de desenvolvimento de APIs REST, incluindo rotas de cadastro de usuário, login e criação/consulta de pedidos. Como projeto ainda não pronto para produção, ele utiliza SQLite local, mas adota padrões de segurança modernos como autenticação baseada em JWT (JSON Web Tokens).

## Autenticação JWT

A aplicação utiliza <em>JWT (JSON Web Tokens)</em> para autenticação sem estado. Em cada login, o servidor gera um token assinado contendo os dados do usuário, que deve ser enviado nas requisições subsequentes. Um JWT é um formato padronizado para codificar objetos JSON como um texto compacto. O token não é criptografado, mas é assinado para garantir sua integridade. Nas rotas protegidas, o token é enviado no cabeçalho HTTP <mark> Authorization </mark> com o prefixo <mark> Bearer</mark>. Por exemplo:
```
    Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```
## Tecnologias Utilizadas
<ul>
    <li><strong>Python 3.x</strong> – linguagem de programação principal.</li>
    <li><strong>FastAPI</strong> – framework web moderno para APIs REST (instalável via pip install fastapi).</li>
    <li><strong>Uvicorn</strong> – servidor ASGI rápido para rodar a aplicação FastAPI (instalável via pip install uvicorn).</li>
    <li><strong>SQLAlchemy</strong> – ORM para mapeamento objeto-relacional, facilitando a interação com o banco de dados.</li>
    <li><strong>SQLite</strong> – banco de dados relacional leve usado neste protótipo para facilitar testes locais.</li>
    <li><strong>PyJWT</strong> – biblioteca para gerar e verificar tokens JWT em Python.</li>
    <li><strong>PassLib (bcrypt)</strong> – biblioteca para hashing de senhas de forma segura.</li>
    <li><strong>Pydantic</strong> – usado pelo FastAPI para validação de dados em modelos.</li>
</ul>

## Instalação da APO localmente

1. Clone o repositório.
```
    git clone https://github.com/Johsep06/delivery-api.git
```

2. Instale as bibliotecas.
```
    pip install -r requirements.txt
```

3. Usar o alembic para migração do banco de dados (opcional)
```
    alembic init alembic
    alembic revision --autogenerate -m "first migration"
```

4. Na raiz do sistema criar o arquivo .env e preencher com variáveis de ambiente com os dados necessários
```
    SECRET_KEY=
    ALGORITHM=
    ACCESS_TOKEN_EXPIRE_MINUTES=
```

5. Executar o programa
```
    uvicorn main:app --reload
```

<h2>Acesse a rota /docs para ler a documentação da api com mais detalhes</h2>
