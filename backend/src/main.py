from contextlib import asynccontextmanager

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.cache import cache_invalidate_all, close_redis
from src.config import settings
from src.notion.client import notion_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    import asyncio
    from src.notion.sync import sync_loop

    sync_task = asyncio.create_task(sync_loop())
    yield
    sync_task.cancel()
    await notion_client.close()
    await close_redis()


app = FastAPI(title="Blog API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
from src.api.posts import router as posts_router  # noqa: E402

app.include_router(posts_router)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/api/cache/invalidate")
async def invalidate_cache(authorization: str = Header()):
    """Bust the entire blog cache. Protected by shared secret."""
    expected = f"Bearer {settings.cache_invalidate_secret}"
    if authorization != expected:
        raise HTTPException(status_code=401, detail="Invalid secret")
    count = await cache_invalidate_all()
    return {"invalidated": count}
