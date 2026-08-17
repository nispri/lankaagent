"""
LankaAgent — Async Database Engine & Session
"""
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

engine = create_async_engine(
    str(settings.DATABASE_URL),
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_pre_ping=True,
    echo=settings.DEBUG,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base model class for all SQLAlchemy models"""
    pass


async def get_session() -> AsyncSession:  # type: ignore[misc]
    """Dependency injection for database sessions"""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def check_db_connection() -> bool:
    """Check database connectivity"""
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


async def setup_rls() -> None:
    """Enable Row Level Security on all tenant-scoped tables."""
    # This should be called on application startup
    async with async_session_factory() as session:
        # Tables that need RLS with tenant_id column (exclude tenants table itself)
        rls_tables = [
            "users",
            "tours",
            "hotels",
            "leads",
            "conversations",
        ]
        
        for table in rls_tables:
            # Enable RLS
            await session.execute(text(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;"))
            
            # Create policy if not exists
            policy_sql = f"""
            DO $$ BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_policies 
                    WHERE tablename = '{table}' AND policyname = 'tenant_isolation'
                ) THEN
                    CREATE POLICY tenant_isolation ON {table}
                        USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
                END IF;
            END $$;
            """
            await session.execute(text(policy_sql))
        
        # Enable RLS on tenants table but with different policy (id-based)
        await session.execute(text("ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;"))
        
        # Create policy for tenants table (based on id)
        tenants_policy = """
        DO $$ BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_policies 
                WHERE tablename = 'tenants' AND policyname = 'tenant_isolation'
            ) THEN
                CREATE POLICY tenant_isolation ON tenants
                    USING (id = current_setting('app.current_tenant_id')::uuid);
            END IF;
        END $$;
        """
        await session.execute(text(tenants_policy))
        
        await session.commit()
        logger.info("RLS policies enabled on all tenant-scoped tables")


async def check_db_connection() -> bool:
    """Check database connectivity"""
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
