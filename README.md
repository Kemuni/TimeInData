# TimeInData

## The goal
Currently, we are living in the fast world, full of work and tasks, so there is a 
question: Have you ever been thinking about how much time do you spend for work or 
spend it on yourself? My projects related to answer on this question and show it 
clearly via user-friendly UI and visual graphs.

## About the project
This repository consist of 3 projects: main database, which will store all users time 
data, telegram bot and website for web apps, as well as interact directly to the database.

My bot will ask every specific period of time that the user is doing now to store this info 
in the database. If the user too busy or the bot will be too annoying, user can turn off 
this reminder and set this information later, for example at the end of the day. After
spending some time fulling data about themselves, the user will be able to overview all data in 
day/week/month/year graphs.

### Telegram bot features
- remind user to set his action type every specific period
- get images of graphs

### Website features
- a convenient way to fill all data about user actions
- interactive graphs


### Sources
[The author][idea_author] of this idea is a guy from reddit, who created a huge graph, based on his 
time spending.

[idea_author]: https://www.reddit.com/r/dataisbeautiful/comments/13pbi6v/oc_how_i_spent_every_hour_of_an_entire_year


## Guides

### How to run Celery Service
1. Run Celery beat with
    ```bash
   celery -A celery_service.tasks beat --loglevelINFO
   ```
2. Run Celery worker with
    ```bash
    celery -A celery_service.tasks beat --loglevelINFO
    ```

