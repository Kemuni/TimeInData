from typing import Optional

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from database import func
from database.models import User


class BaseRepo:
    """ A class representing a base repository for handling database operations. """

    def __init__(self, session: AsyncSession):
        self.session = session


class UserRepo(BaseRepo):
    async def get_or_create_user(self, user_id: int, language: str, username: Optional[str] = None) -> Optional[User]:
        """
        Creates or updates a new user in the database and returns the user object.
        :param user_id: The user's ID.
        :param language: The user's language.
        :param username: The user's username. It's an optional parameter.
        :return: User object, None if there was an error while making a transaction.
        """

        insert_stmt = (
            insert(User)
            .values(
                user_id=user_id,
                username=username,
                language=language,
            )
            .on_conflict_do_update(
                index_elements=[User.user_id],
                set_=dict(
                    username=username,
                    language=language,
                    last_activity=func.utcnow(),
                ),
            )
            .returning(User)
        )

        result = await self.session.execute(insert_stmt)

        await self.session.commit()
        return result.scalar_one()


class DatabaseRepo(BaseRepo):
    """
    Repository for handling database operations. This class holds all the repositories for the database models.
    """

    @property
    def users(self) -> UserRepo:
        return UserRepo(self.session)
