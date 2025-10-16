[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/5CXfCXPo)

Funcionalidades do projeto

1) Procurar ações por nome ou ticker
2) Ver preço da ação e variação (exibe, também, data e horário da última atualização)
3) Salvar a ação em uma watchlist com base em uma meta de preço e observação (comprar/vender) -> fica vermelha caso atinja a meta (para chamar a atenção do usuário)


APIS utilizadas:

1) brapi.dev (B3 – principal para ações .SA)

    Base: https://brapi.dev/api

    Endpoints usados:

    Busca:
    GET /search?query=PETR

    Cotação/quote:
    GET /quote/PETR4?range=1d&interval=1d&fundamental=true&token=SEU_TOKEN

    Observação: precisa de token (BRAPI_TOKEN) — você já configurou.

2) Yahoo Finance (não-oficial – primário p/ EUA, fallback p/ B3)

    Bases:
    https://query1.finance.yahoo.com
    https://query2.finance.yahoo.com

    Endpoints usados:

    Busca:
    GET /v1/finance/search?q=AAPL&quotesCount=10

    Cotação/quote:
    GET /v7/finance/quote?symbols=AAPL
    GET /v7/finance/quote?symbols=PETR4.SA

    Observação: requer headers de navegador (User-Agent) e às vezes retorna 401/403 → por isso temos fallback.

3) Stooq (fallback sem chave para ações dos EUA)

    Base: https://stooq.com

    Endpoint usado (CSV diário):

    GET /q/d/l/?s=aapl.us&i=d

    Observação: retorna CSV; usei os dois últimos “Close” para preço/variação. Símbolo em minúsculas com sufixo .us.


----------------------------
env\Scripts\activate
python manage.py runserver 

gerar migrações
python manage.py makemigrations notes

aplicar no banco
python manage.py migrate


Trocar no settings para rodar no render
DATABASES = {
    'default': dj_database_url.config(
        default='postgresql://exemplo_prj1b_user:vCvVTXQPY8MSTCTUjkBxXQcKsdfAsqIJ@dpg-d31fjfqdbo4c73a7p4eg-a.oregon-postgres.render.com/exemplo_prj1b',
        conn_max_age=600,
        ssl_require=not DEBUG
    )
}