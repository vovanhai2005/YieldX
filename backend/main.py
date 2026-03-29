from fastapi import FastAPI
from domains.gold import router as gold_router

app = FastAPI(
    title="YIELDX API",
    description="API theo dõi tỷ suất sinh lời các tài sản tại Việt Nam",
    version="1.0.0"
)

app.include_router(gold_router.router)

@app.get("/")
async def root():
    return {"message": "Welcome to the YIELDX API. Use /docs for API documentation."}