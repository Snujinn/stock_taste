from fastapi import APIRouter
from app.api.endpoints import auth, market, trade, portfolio

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(market.router, prefix="/market", tags=["market"])
api_router.include_router(trade.router, prefix="/trade", tags=["trade"])
api_router.include_router(portfolio.router, prefix="/portfolio", tags=["portfolio"])
from app.api.endpoints import leaderboard
api_router.include_router(leaderboard.router, prefix="/leaderboard", tags=["leaderboard"])
