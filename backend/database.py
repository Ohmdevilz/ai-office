import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = "https://lwzkwaudoefhbdefmmhe.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


def get_client() -> Client:
    if not SUPABASE_KEY:
        raise ValueError("SUPABASE_KEY not found. Please set it in the .env file.")
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def save_conversation(agent: str, task: str, result: str, expected_output: str | None = None) -> dict:
    client = get_client()
    record = {
        "agent": agent,
        "task": task,
        "result": result,
        "expected_output": expected_output,
    }
    response = client.table("conversations").insert(record).execute()
    return response.data[0] if response.data else {}


def get_history(agent: str, limit: int = 20) -> list[dict]:
    client = get_client()
    response = (
        client.table("conversations")
        .select("id, agent, task, expected_output, result, created_at")
        .eq("agent", agent)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return response.data or []
