"""
perplexity_service.py
ดึงข้อมูล real-time 2 ส่วนสำหรับ Trader Agent:
  1. Economic Calendar — High Impact events สัปดาห์นี้ที่กระทบทองคำ
  2. Gold News — ข่าวล่าสุด 24-48 ชม. ที่กระทบ XAU/USD
"""
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date

import requests

logger = logging.getLogger(__name__)

_API_BASE = "https://api.perplexity.ai/chat/completions"
_MODEL = "sonar"
_TIMEOUT = 40  # seconds


def _query(prompt: str, api_key: str) -> str:
    resp = requests.post(
        _API_BASE,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": _MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
        },
        timeout=_TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def fetch_economic_calendar(api_key: str) -> str:
    """ดึง Economic Calendar High Impact สัปดาห์นี้ที่กระทบทองคำ"""
    today = date.today().strftime("%Y-%m-%d")
    prompt = (
        f"วันนี้คือ {today} "
        "ดึงข้อมูล Economic Calendar สัปดาห์นี้ (7 วัน) "
        "เฉพาะรายการ High Impact ที่กระทบทองคำ (XAU/USD) ได้แก่ "
        "NFP, CPI, Core CPI, PCE, FOMC Meeting/Minutes/Statement, Fed Chair Speech, "
        "GDP, ISM Manufacturing/Services, Retail Sales, PPI, Initial Jobless Claims, "
        "ADP Non-Farm, Jackson Hole และ High Impact อื่นๆ "
        "สำหรับแต่ละรายการระบุ: วันที่, เวลา (GMT+7), "
        "Actual (ถ้ามี), Forecast, Previous, "
        "และผลกระทบต่อทองคำ (Bullish/Bearish/Neutral + เหตุผลสั้น) "
        "ตอบเป็นภาษาไทย จัดรูปแบบเป็นตาราง"
    )
    return _query(prompt, api_key)


def fetch_gold_news(api_key: str) -> str:
    """ดึงข่าวล่าสุด 24-48 ชั่วโมงที่กระทบ XAU/USD"""
    today = date.today().strftime("%Y-%m-%d")
    prompt = (
        f"วันนี้คือ {today} "
        "ค้นหาข่าวสำคัญ 24-48 ชั่วโมงที่ผ่านมาที่กระทบราคาทองคำ (XAU/USD) ครอบคลุม: "
        "1) คำพูดหรือโพสต์ล่าสุดของ Donald Trump เกี่ยวกับนโยบายการค้า ภาษี tariff เศรษฐกิจ "
        "2) ความตึงเครียด Geopolitical (รัสเซีย-ยูเครน ตะวันออกกลาง เกาหลีเหนือ ไต้หวัน) "
        "3) ความเคลื่อนไหวของ Fed (Fed speakers, hawkish/dovish signals) "
        "4) ความเสี่ยง Risk-On/Risk-Off ในตลาดโลก "
        "5) ข่าวอื่นๆ ที่ส่งผลต่อ Safe Haven demand "
        "แต่ละข่าวระบุ: หัวข้อ, วันที่/เวลา, สรุปสาระสำคัญ, "
        "ผลกระทบต่อทองคำ (Bullish/Bearish + เหตุผล) "
        "ตอบเป็นภาษาไทย"
    )
    return _query(prompt, api_key)


def fetch_market_context(api_key: str) -> str:
    """รัน fetch_economic_calendar และ fetch_gold_news พร้อมกัน แล้วรวมเป็น context block"""
    results = {"calendar": "", "news": ""}
    errors = []

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {
            executor.submit(fetch_economic_calendar, api_key): "calendar",
            executor.submit(fetch_gold_news, api_key): "news",
        }
        for future in as_completed(futures):
            key = futures[future]
            try:
                results[key] = future.result()
            except Exception as exc:
                logger.warning("Perplexity fetch failed for %s: %s", key, exc)
                errors.append(key)

    sections = []

    if results["calendar"]:
        sections.append(
            "=== ECONOMIC CALENDAR — HIGH IMPACT (สัปดาห์นี้) ===\n"
            f"{results['calendar']}\n"
            "=== END ECONOMIC CALENDAR ==="
        )
    elif "calendar" in errors:
        sections.append("=== ECONOMIC CALENDAR: ไม่สามารถดึงข้อมูลได้ ===")

    if results["news"]:
        sections.append(
            "=== GOLD NEWS — ข่าวล่าสุด 24-48 ชม. ===\n"
            f"{results['news']}\n"
            "=== END GOLD NEWS ==="
        )
    elif "news" in errors:
        sections.append("=== GOLD NEWS: ไม่สามารถดึงข้อมูลได้ ===")

    if not sections:
        return ""

    return "\n\n".join(sections) + "\n"
