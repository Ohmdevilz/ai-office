import asyncio
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from secretary_pool import run_marketing_task, run_trader_task
from database import save_conversation, get_history

app = FastAPI(title="AI Office API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Request / Response Models ───────────────────────────────────────────────

class TaskRequest(BaseModel):
    task: str
    expected_output: str | None = None


class TaskResponse(BaseModel):
    agent: str
    result: str


class HistoryItem(BaseModel):
    id: str
    agent: str
    task: str
    expected_output: str | None
    result: str
    created_at: str


# ─── Endpoints ───────────────────────────────────────────────────────────────

@app.get("/")
def health():
    return {"status": "ok", "service": "AI Office"}


@app.post("/api/marketing", response_model=TaskResponse)
async def marketing_endpoint(body: TaskRequest):
    """ส่งงานให้ Marketing Executive Secretary วิเคราะห์/สรุปข้อมูลการตลาด"""
    try:
        kwargs = {"task_description": body.task}
        if body.expected_output:
            kwargs["expected_output"] = body.expected_output

        result = await asyncio.to_thread(run_marketing_task, **kwargs)
        await asyncio.to_thread(save_conversation, "marketing", body.task, result, body.expected_output)
        return TaskResponse(agent="marketing", result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/marketing/history", response_model=list[HistoryItem])
async def marketing_history(limit: int = Query(default=20, le=100)):
    """ดึงประวัติการสนทนาของ Marketing Secretary"""
    try:
        return await asyncio.to_thread(get_history, "marketing", limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/trader", response_model=TaskResponse)
async def trader_endpoint(body: TaskRequest):
    """ส่งงานให้ Trader Personal Secretary วิเคราะห์กราฟ/จุดเข้าออเดอร์"""
    try:
        kwargs = {"task_description": body.task}
        if body.expected_output:
            kwargs["expected_output"] = body.expected_output

        result = await asyncio.to_thread(run_trader_task, **kwargs)
        await asyncio.to_thread(save_conversation, "trader", body.task, result, body.expected_output)
        return TaskResponse(agent="trader", result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/trader/history", response_model=list[HistoryItem])
async def trader_history(limit: int = Query(default=20, le=100)):
    """ดึงประวัติการสนทนาของ Trader Secretary"""
    try:
        return await asyncio.to_thread(get_history, "trader", limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
