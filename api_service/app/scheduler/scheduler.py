from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import get_config

scheduler = AsyncIOScheduler(jobstores={'default': SQLAlchemyJobStore(url=get_config().db.job_store_url)})

