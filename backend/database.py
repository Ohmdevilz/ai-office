import os
import re
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


def search_knowledge_base(query: str, limit: int = 5) -> list[dict]:
    """ค้นหา KB chunks ที่เกี่ยวข้องกับ query โดยใช้ keyword matching บน topic_tags และ content"""
    client = get_client()

    # แยก keywords จาก query (ตัดคำสั้นกว่า 2 ตัวออก, lowercase)
    raw_keywords = re.split(r"[\s,/\-\(\)]+", query.lower())
    keywords = [k for k in raw_keywords if len(k) >= 2][:10]

    if not keywords:
        # fallback: คืน PART 4 (SMC) ทั้งหมด
        resp = (
            client.table("knowledge_base")
            .select("part_number, part_name, section_number, section_title, content")
            .eq("part_number", 4)
            .limit(limit)
            .execute()
        )
        return resp.data or []

    # ค้นด้วย OR: ถ้า keyword ใดอยู่ใน topic_tags หรือ section_title หรือ content
    # Supabase PostgREST รองรับ .contains() สำหรับ array และ .ilike() สำหรับ text
    seen_sections: set[str] = set()
    results: list[dict] = []

    # รอบแรก: หาจาก topic_tags (precise match)
    for kw in keywords:
        if len(results) >= limit:
            break
        resp = (
            client.table("knowledge_base")
            .select("part_number, part_name, section_number, section_title, content")
            .contains("topic_tags", [kw])
            .limit(limit)
            .execute()
        )
        for row in (resp.data or []):
            if row["section_number"] not in seen_sections:
                seen_sections.add(row["section_number"])
                results.append(row)

    # รอบสอง: หาจาก section_title + content (fuzzy)
    if len(results) < limit:
        for kw in keywords:
            if len(results) >= limit:
                break
            for field in ("section_title", "content"):
                resp = (
                    client.table("knowledge_base")
                    .select("part_number, part_name, section_number, section_title, content")
                    .ilike(field, f"%{kw}%")
                    .limit(limit)
                    .execute()
                )
                for row in (resp.data or []):
                    if row["section_number"] not in seen_sections:
                        seen_sections.add(row["section_number"])
                        results.append(row)

    return results[:limit]


def format_kb_context(chunks: list[dict]) -> str:
    """แปลง KB chunks เป็น string context สำหรับใส่ใน prompt"""
    if not chunks:
        return ""
    parts = ["=== KNOWLEDGE BASE REFERENCE ==="]
    for chunk in chunks:
        parts.append(
            f"\n[PART {chunk['part_number']}: {chunk['part_name']} — {chunk['section_number']} {chunk['section_title']}]\n"
            f"{chunk['content']}\n"
            f"{'—' * 60}"
        )
    parts.append("=== END KNOWLEDGE BASE ===\n")
    return "\n".join(parts)
