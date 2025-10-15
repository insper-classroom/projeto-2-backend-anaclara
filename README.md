[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/5CXfCXPo)

LINK API https://site.financialmodelingprep.com/developer/docs

API KEY: rkWdx3KpAZ7tQQQTfPTExAywPhYvnGAr


abrir docker
docker run --rm --name pg-docker -e POSTGRES_PASSWORD=escolhaumasenha -d -p 5432:5432 -v $HOME/docker/volumes/postgres:/var/lib/postgresql/data postgres
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