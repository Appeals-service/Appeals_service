import jwt
from fastapi import Request, HTTPException, status, Depends
from user_agents import parse

from src.common.settings import settings
from src.utils.enums import TokenType, UserRole


def get_token(request: Request) -> str:
    if not (token := request.cookies.get("access_token")):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token not found")
    return token


def get_user_agent(request: Request):
    return request.headers["user-agent"]


def get_current_user_data(
        token: str = Depends(get_token), current_user_agent: str = Depends(get_user_agent)
) -> dict[str, str | UserRole]:
    check_token_type(token, TokenType.access)

    try:
        payload = jwt.decode(token, key=settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except jwt.PyJWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    if (
            not (role := payload.get("role")) or
            not (user_id := payload.get("sub")) or
            not (user_agent := payload.get("user_agent"))
    ):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    if str(parse(current_user_agent)) != user_agent:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token data")

    try:
        role = getattr(UserRole, role)
    except AttributeError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token data")

    return {"id": user_id, "role": role}


def check_token_type(token: str, required_type: TokenType) -> None:
    header = jwt.get_unverified_header(token)
    if (token_type := header.get("typ")) and token_type != required_type:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token data")
