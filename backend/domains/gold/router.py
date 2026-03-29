from fastapi import APIRouter

router = APIRouter(
    prefix="/gold",
    tags=["Gold Price"],
)

@router.get("/latest")
async def get_latest_gold_price():
    return {
        "asset": "SJC Gold",
        "buy_price": 80000000,
        "sell_price": 82000000,
        "source": "SJC",
        "timestamp": "2026-03-08T12:00:00Z"
    }