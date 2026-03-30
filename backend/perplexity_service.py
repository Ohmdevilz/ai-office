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
        f"วันนี้คือ {today} (วันจันทร์ถึงศุกร์ของสัปดาห์นี้) "
        "ค้นหาจาก Forex Factory (forexfactory.com) หรือ Investing.com economic calendar "
        "แล้วดึงรายการ High Impact ทุกรายการของสัปดาห์นี้ที่กระทบทองคำ (XAU/USD) "
        "โดยต้องครอบคลุมรายการเหล่านี้ถ้ามีในสัปดาห์นี้:\n"
        "- NFP (Non-Farm Payrolls)\n"
        "- ADP Non-Farm Employment Change\n"
        "- JOLTS Job Openings\n"
        "- Initial Jobless Claims\n"
        "- CPI (Consumer Price Index) และ Core CPI\n"
        "- PPI (Producer Price Index)\n"
        "- PCE Price Index (Core PCE)\n"
        "- Retail Sales\n"
        "- ISM Manufacturing PMI / ISM Services PMI\n"
        "- GDP\n"
        "- FOMC Meeting, Statement, Minutes หรือ Rate Decision\n"
        "- Fed Chair Powell Speech หรือ Fed Member speeches\n"
        "- ข่าว High Impact อื่นๆ ที่กระทบ USD หรือทองคำ\n\n"
        "สำหรับแต่ละรายการให้ระบุครบทุกคอลัมน์:\n"
        "| วันที่ | เวลา (GMT+7) | รายการ | Actual | Forecast | Previous | ผลกระทบต่อทองคำ |\n"
        "ถ้า Actual ยังไม่ออก ให้ใส่ '-' แต่ Forecast และ Previous ต้องระบุค่าจริงเสมอ "
        "ผลกระทบต่อทองคำให้วิเคราะห์ว่า Bullish / Bearish / Neutral พร้อมเหตุผลสั้นๆ "
        "ตอบเป็นภาษาไทย จัดในรูปแบบตารางที่อ่านง่าย"
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
