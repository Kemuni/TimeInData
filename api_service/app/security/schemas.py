from typing import Annotated

from annotated_doc import Doc
from pydantic import BaseModel


class HTTPTMACredentials(BaseModel):
    user_id: Annotated[
        int,
        Doc("The TMA Init Data Authorization user ID extracted from the headers value.")
    ]
    username: Annotated[
        str,
        Doc("The TMA Init Data Authorization username extracted from the headers value.")
    ]
    language_code: Annotated[
        str,
        Doc("The TMA Init Data Authorization language code extracted from the headers value.")
    ]


class HTTPUserCredentials(BaseModel):
    user_id: Annotated[
        int,
        Doc("The HTTP user ID extracted from the headers value.")
    ]
    username: Annotated[
        str,
        Doc("The HTTP username extracted from the headers value.")
    ]
    language_code: Annotated[
        str,
        Doc("The HTTP language code extracted from the headers value.")
    ]