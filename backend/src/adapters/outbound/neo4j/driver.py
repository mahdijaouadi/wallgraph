from neo4j import AsyncGraphDatabase, AsyncDriver, AsyncSession
from backend.src.config.settings import settings
from typing import Optional

# Drivers for admin and read-only users
_admin_driver: Optional[AsyncDriver] = None
_readonly_driver: Optional[AsyncDriver] = None


async def init_driver() -> None:
    global _admin_driver, _readonly_driver

    if _admin_driver is None:
        _admin_driver = AsyncGraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_adminuser, settings.neo4j_adminpassword),
        )
        await _admin_driver.verify_authentication()

    if _readonly_driver is None:
        _readonly_driver = AsyncGraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_readonlyuser, settings.neo4j_readonlypassword),
        )
        await _readonly_driver.verify_authentication()


async def close_driver() -> None:
    global _admin_driver, _readonly_driver
    if _admin_driver is not None:
        await _admin_driver.close()
        _admin_driver = None
    if _readonly_driver is not None:
        await _readonly_driver.close()
        _readonly_driver = None


def get_admin_driver() -> AsyncDriver:
    if _admin_driver is None:
        raise RuntimeError("Admin driver not initialized. Ensure app lifespan started.")
    return _admin_driver


def get_readonly_driver() -> AsyncDriver:
    if _readonly_driver is None:
        raise RuntimeError("Read-only driver not initialized. Ensure app lifespan started.")
    return _readonly_driver


async def get_admin_session() -> AsyncSession:
    driver = get_admin_driver()
    return driver.session(database=settings.neo4j_database)


async def get_readonly_session() -> AsyncSession:
    driver = get_readonly_driver()
    return driver.session(database=settings.neo4j_database)
