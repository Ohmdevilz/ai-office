"""
perplexity_service.py
ดึงข้อมูล real-time 2 ส่วนสำหรับ Trader Agent โดยใช้ Perplexity sonar-pro:
  1. Economic Calendar — ข่าว USD High Impact วันนี้ถึงศุกร์ จาก Forex Factory
  2. Gold News — ข่าวล่าสุด 24-48 ชม. ที่กระทบ XAU/USD
"""
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date

import requests

logger = logging.getLogger(__name__)

_API_BASE = "https://api.perplexity.ai/chat/completions"
_MODEL = "sonar-pro"
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
    """ดึง Economic Calendar USD High Impact วันนี้ถึงศุกร์ จาก Forex Factory ผ่าน Perplexity"""
    today = date.today().strftime("%Y-%m-%d")
    friday = "ศุกร์นี้"
    prompt = (
        f"วันนี้คือ {today} "
        f"ค้นหาจาก Forex Factory (forexfactory.com) ว่าตั้งแต่วันนี้ถึง{friday} "
        "มีข่าว USD High Impact อะไรบ้าง "
        "โดยเฉพาะรายการต่อไปนี้ถ้ามีในสัปดาห์นี้: "
        "NFP (Non-Farm Payrolls), ADP Non-Farm Employment Change, "
        "JOLTS Job Openings, Initial Jobless Claims (Unemployment Claims), "
        "CB Consumer Confidence, ISM Manufacturing PMI, ISM Services PMI, "
        "Retail Sales, Core Retail Sales, CPI, Core CPI, PPI, PCE, Core PCE, "
        "GDP, FOMC Meeting/Statement/Minutes, Fed Chair Powell Speech, "
        "Fed Member speeches, Average Hourly Earnings, Unemployment Rate\n\n"
        "สำหรับแต่ละรายการให้ระบุ:\n"
        "- วันที่และเวลา (GMT+7)\n"
        "- ชื่อข่าว\n"
        "- Forecast (ถ้ามี)\n"
        "- Previous\n"
        "- ผลกระทบต่อทองคำ: ถ้า Actual ออกมาดีกว่า Forecast → USD แข็ง → ทองลง (Bearish Gold) "
        "/ ถ้าแย่กว่า → USD อ่อน → ทองขึ้น (Bullish Gold) / Speech ให้ระบุว่า Hawkish หรือ Dovish\n\n"
        "จัดในรูปแบบตารางที่อ่านง่าย ตอบเป็นภาษาไทย"
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
    """รัน fetch_economic_calendar และ fetch_gold_news พร้อมกันผ่าน Perplexity sonar-pro"""
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
