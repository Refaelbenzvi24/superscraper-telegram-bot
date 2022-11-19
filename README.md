# Superscraper-telegram-bot

## Table Of Content

- [Description](#Description)
- [Project Content](#Project-Content)
    - [Libraries](#Libraries)
    - [Structure](#Structure)
- [Running the service](#Running-the-service)

## Description

This's a telegram bot that scrapes the web for you.

currently, it supports the following:

- [TerminalX](https://terminalx.com/) <br/>
    - shoes <br/>

## Project Content

### Libraries

- [PDM](https://pdm.fming.dev/latest/)
- [Celery](https://docs.celeryq.dev/)
- [RabbitMQ](https://www.rabbitmq.com/)
- [PostgreSQL](https://www.postgresql.org/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Docker](https://www.docker.com/)
- [PyQuery](https://pythonhosted.org/pyquery/)

### Structure

```shell
src
├── bot # bot module
|    ├── controllers # bot controllers
|    ├── controllers # bot conversations
|    └── main.py # bot main file
├── celery
|    ├── beat.py # celery beat scheduler main file
|    └── worker.py # celery worker main file
├── config
└── shared
     ├── models # shared sqlalchemy models
     └── tasks # shared celery tasks
df_bot.Dockerfile # Dockerfile for the bot
df_worker.Dockerfile # Dockerfile for the celery worker
df_beat.Dockerfile # Dockerfile for the celery beat scheduler
docker-compose.yml # docker-compose file
```

## Running the service

clone the repo `git clone git@github.com:Refaelbenzvi24/superscraper-telegram-bot.git`

then

```shell
cd Superscraper-telegram-bot
cp .env.example .env
```

add your telegram bot `TOKEN` and `BOT_ACCESS_PASSWORD` to the `.env` file

```shell
docker compose up
```

