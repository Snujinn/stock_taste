from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core import database
from app.models.user import User
from app.api import deps
from app.core.config import settings
import redis.asyncio as redis

router = APIRouter()

@router.get("/")
async def get_leaderboard(limit: int = 50) -> Any:
    r = redis.from_url(settings.REDIS_URL, decode_responses=True)
    try:
        # Get Top N
        leaderboard_data = await r.zrevrange("leaderboard", 0, limit - 1, withscores=True)
        
        results = []
        for user_id, score in leaderboard_data:
             nickname = await r.hget("user_nicknames", user_id)
             results.append({
                 "rank": 0, # assigned by index
                 "nickname": nickname or "Unknown",
                 "total_equity_krw": int(score)
             })
        
        # Assign ranks
        for i, res in enumerate(results):
            res['rank'] = i + 1
            
        return results
    finally:
        await r.aclose()

@router.get("/me")
async def get_my_rank(current_user: User = Depends(deps.get_current_user)) -> Any:
    r = redis.from_url(settings.REDIS_URL, decode_responses=True)
    try:
        rank = await r.zrevrank("leaderboard", str(current_user.id))
        score = await r.zscore("leaderboard", str(current_user.id))
        
        return {
            "rank": (rank + 1) if rank is not None else -1,
            "total_equity_krw": int(score) if score else 0
        }
    finally:
        await r.aclose()
