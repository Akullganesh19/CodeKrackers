from typing import Optional
from pydantic import BaseModel

class Token(BaseModel):  # noqa: E302
    access_token: str
    token_type: str

class TokenPayload(BaseModel):  # noqa: E302
    sub: Optional[int] = None
