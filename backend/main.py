import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from secretary_pool import run_marketing_task, run_trader_task

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
        return TaskResponse(agent="marketing", result=result)
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
        return TaskResponse(agent="trader", result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
