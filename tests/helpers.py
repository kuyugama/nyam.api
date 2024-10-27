import secrets
from datetime import timedelta
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

import src
import src.permissions
from src.util import now, secure_hash
from src.models import User, Token, Role


async def create_role(
    session: AsyncSession,
    name: str,
    default: bool = False,
    description: str = "Description",
    permissions: dict[str, bool] = None,
) -> Role:
    if permissions is None:
        permissions = {
            src.permissions.user.own.update_info: True,
        }

    role = Role(
        name=name,
        description=description,
        default=default,
        permissions=permissions,
    )
    session.add(role)

    await session.commit()

    return role


async def create_user(
    session: AsyncSession, email: str, nickname: str, password: str, role: Role
) -> User:
    user = User(
        email=email,
        nickname=nickname,
        password_hash=secure_hash(password),
        role=role,
    )

    session.add(user)
    await session.commit()

    return user


async def create_token(
    session: AsyncSession, user: User, valid_for: timedelta = timedelta(hours=6)
) -> Token:
    token = Token(
        owner_id=user.id,
        expire_at=now() + valid_for,
        body=secrets.token_hex(64),
    )
    session.add(token)
    await session.commit()

    return token


def assert_contain(source: dict[str, Any], **kw):
    for name, value in kw.items():
        actual_value = source.get(name)
        if actual_value != value:
            print("[-] assert_contain call:")
            print("[+] Name:", name)
            print("[+] Actual value:", actual_value)
            print("[+] Expected value:", value)
            print("[-] assert_contain call end")
        assert actual_value == value
