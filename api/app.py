from fastapi import FastAPI
from api.routers import routers_list

app = FastAPI()
for router in routers_list:
    app.include_router(router)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app)
