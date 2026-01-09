# TimeInData
[![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=fff)](https://www.docker.com)
[![Pytest](https://img.shields.io/badge/Pytest-fff?logo=pytest&logoColor=000)](https://docs.pytest.org/en/)
[![FastAPI](https://img.shields.io/badge/FastAPI-white?logo=fastapi&logoColor=#009688)](https://fastapi.tiangolo.com)
[![aiogram](https://img.shields.io/badge/aiogram-gray?logo=aiogram&logoColor=#26A5E4)](https://github.com/aiogram/aiogram)
[![React](https://img.shields.io/badge/React-%2320232a.svg?logo=react&logoColor=%2361DAFB)](https://reactjs.org)
[![Postgres](https://img.shields.io/badge/Postgres-%23316192.svg?logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-%23DD0031.svg?logo=redis&logoColor=white)](https://redis.io)
[![RabbitMQ](https://img.shields.io/badge/RabbitMQ-white?logo=rabbitmq&logoColor=#FF6600)](https://www.rabbitmq.com)

---
## Installation

1. Clone this repository via 
    ```bash
    git clone https://github.com/Kemuni/TimeInData.git
    ```
2. Copy `example.env` to `.env` and fill it with your data
3. Run `docker compose up -d --build` or `docker compose watch` (for development).

Now you can check next services:
- Adminer: `http://localhost:8070` to manage databases
- API: `http://localhost:8000/docs` to see API docs
- Telegram bot in your Telegram app
- WebApp works only in Telegram app. 

---
## Architecture
The architecture of the project is based on the following components:
- **API service** (FastAPI + SQLAlchemy): Store all data about user actions, provide API and manage scheduled tasks.
- **Telegram bot** (aiogram): Telegram-UI to interact with our application.
- **WebApp** (React.js): Telegram MiniApp with user-friendly UI.
- **PostgreSQL**: Database which stores all our data.
- **Redis**: Cache for Telegram bot and API service.
- **RabbitMQ**: Message broker for scheduled tasks and expensive operations.


### Sources
[The author](https://www.reddit.com/r/dataisbeautiful/comments/13pbi6v/oc_how_i_spent_every_hour_of_an_entire_year) of this idea is a guy from reddit, who created a huge graph, based on his 
time spending.
