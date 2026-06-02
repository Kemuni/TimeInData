# TimeInData
[English version](README_EN.md)<br/>
Сервис для тайм-менеджмента

[![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=fff)](https://www.docker.com)
[![Pytest](https://img.shields.io/badge/Pytest-fff?logo=pytest&logoColor=000)](https://docs.pytest.org/en/)
[![FastAPI](https://img.shields.io/badge/FastAPI-white?logo=fastapi&logoColor=#009688)](https://fastapi.tiangolo.com)
[![aiogram](https://img.shields.io/badge/aiogram-gray?logo=aiogram&logoColor=#26A5E4)](https://github.com/aiogram/aiogram)
[![React](https://img.shields.io/badge/React-%2320232a.svg?logo=react&logoColor=%2361DAFB)](https://reactjs.org)
[![Postgres](https://img.shields.io/badge/Postgres-%23316192.svg?logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-%23DD0031.svg?logo=redis&logoColor=white)](https://redis.io)
[![RabbitMQ](https://img.shields.io/badge/RabbitMQ-white?logo=rabbitmq&logoColor=#FF6600)](https://www.rabbitmq.com)

---
## Суть сервиса

Отслеживание активностей (работа/учеба/отдых и т.д.) каждый час для наглядного просмотра того, на что 
уходит больше всего времени.

---
## Установка

1. Склонировать данный репозиторий с помощью
    ```bash
    git clone https://github.com/Kemuni/TimeInData.git
    ```
2. Скопировать `example.env` в файл `.env` и заполнить его своими данными.
3. Запустить следующую команду, чтобы запустить сервисы:
   ```bash
   docker compose up -d --build
   ```
   или `docker compose watch` для запуска в режиме разработки.

Теперь мы можем использовать следующие сервисы:
- Adminer: `http://localhost:8070` для администрирования БД.
- API: `http://localhost:8000/docs` для получения документации API.
- Telegram бот в приложении Telegram.
- WebApp работает только в Telegram. 

---
## Архитектура
Представлена следующим образом:
![Архитектура](readme_asset/architecture_diagram.svg)
Архитектура основывается на следующих компонентах:
- **API service** (FastAPI + SQLAlchemy): Предоставляет API, где хранит и обрабатывает всю информацию активностей пользователя.
- **Scheduled tasks**: Создает запланированные задачи в брокер сообщений и запускается вместе с API. 
- **Telegram bot** (aiogram): Telegram-бот для взаимодействия с приложением.
- **WebApp** (React.js): Telegram MiniApp с удобным пользовательским UI.
- **PostgreSQL**: База данных, которая хранит всю информацию.
- **Redis**: Кэш для Telegram бота и нашего API.
- **RabbitMQ**: Брокер сообщений для запланированных задач, оповещений и дорогих вычислений.


### Источник
[Автор](https://www.reddit.com/r/dataisbeautiful/comments/13pbi6v/oc_how_i_spent_every_hour_of_an_entire_year) этой идеи - человек из Reddit, который создал большую диаграмму, основанную на его времени и активностях.
