"""
perplexity_service.py
ดึงข้อมูล real-time 2 ส่วนสำหรับ Trader Agent:
  1. Economic Calendar — ดึงโดยตรงจาก Forex Factory JSON (ฟรี, real-time)
  2. Gold News — ข่าวล่าสุด 24-48 ชม. จาก Perplexity sonar
"""
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timedelta, timezone

import requests

logger = logging.getLogger(__name__)

_FF_CALENDAR_URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
_API_BASE = "https://api.perplexity.ai/chat/completions"
_MODEL = "sonar"
_TIMEOUT = 40  # seconds
_TZ_GMT7 = timezone(timedelta(hours=7))
_THAI_DAYS = ["จันทร์", "อังคาร", "พุธ", "พฤหัส", "ศุกร์", "เสาร์", "อาทิตย์"]


# ─── Forex Factory helpers ────────────────────────────────────────────────────

def _to_gmt7(iso_str: str) -> datetime | None:
    try:
        dt = datetime.fromisoformat(iso_str)
        return dt.astimezone(_TZ_GMT7)
    except (ValueError, TypeError):
        return None


def _parse_num(s: str) -> float | None:
    """แปลงค่าตัวเลขแบบ '56K' '6.90M' '0.3%' '-0.2%' เป็น float"""
    if not s:
        return None
    s = s.strip().replace(",", "")
    multiplier = 1.0
    if s.upper().endswith("K"):
        multiplier = 1_000; s = s[:-1]
    elif s.upper().endswith("M"):
        multiplier = 1_000_000; s = s[:-1]
    elif s.upper().endswith("B"):
        multiplier = 1_000_000_000; s = s[:-1]
    s = s.rstrip("%")
    try:
        return float(s) * multiplier
    except ValueError:
        return None


def _gold_signal(title: str, forecast: str, previous: str) -> str:
    """ประเมินทิศทางทองคำเบื้องต้นจาก Forecast เทียบ Previous"""
    f = _parse_num(forecast)
    p = _parse_num(previous)
    if f is None or p is None:
        return "-"

    title_l = title.lower()

    # ค่าสูง = USD อ่อน = ทองขึ้น (inverted)
    inverted = {"unemployment", "jobless claims", "claims"}
    # ค่าสูง = USD แข็ง = ทองลง
    standard = {
        "non-farm", "adp", "gdp", "retail", "ism", "pmi", "jolts",
        "job openings", "hourly earnings", "consumer confidence",
        "cpi", "ppi", "pce", "inflation", "price index", "housing",
    }

    is_inv = any(k in title_l for k in inverted)
    is_std = any(k in title_l for k in standard)

    if is_inv:
        if f > p: return "🟢 Bullish Gold (USD อ่อน)"
        if f < p: return "🔴 Bearish Gold (USD แข็ง)"
        return "⚪ Neutral"
    if is_std:
        if f > p: return "🔴 Bearish Gold (USD แข็ง)"
        if f < p: return "🟢 Bullish Gold (USD อ่อน)"
        return "⚪ Neutral"
    return "-"


def fetch_economic_calendar() -> str:
    """ดึง Economic Calendar USD High Impact สัปดาห์นี้จาก Forex Factory JSON"""
    resp = requests.get(
        _FF_CALENDAR_URL,
        timeout=15,
        headers={"User-Agent": "Mozilla/5.0"},
    )
    resp.raise_for_status()
    events = resp.json()

    filtered = sorted(
        [e for e in events if e.get("country") == "USD" and e.get("impact") == "High"],
        key=lambda e: e.get("date", ""),
    )

    if not filtered:
        return "ไม่พบรายการ High Impact USD ในสัปดาห์นี้"

    lines = [
        "| วัน | วันที่ | เวลา (GMT+7) | รายการ | Actual | Forecast | Previous | สัญญาณทอง |",
        "|---|---|---|---|---|---|---|---|",
    ]

    for e in filtered:
        dt = _to_gmt7(e.get("date", ""))
        if dt:
            day_th = _THAI_DAYS[dt.weekday()]
            date_str = dt.strftime("%d/%m")
            time_str = dt.strftime("%H:%M")
        else:
            day_th = date_str = time_str = "-"

        title    = e.get("title", "-")
        actual   = e.get("actual") or "-"
        forecast = e.get("forecast") or "-"
        previous = e.get("previous") or "-"
        signal   = _gold_signal(title, e.get("forecast", ""), e.get("previous", ""))

        lines.append(
            f"| {day_th} | {date_str} | {time_str} | {title} "
            f"| {actual} | {forecast} | {previous} | {signal} |"
        )

    lines += [
        "",
        "*หมายเหตุ: Actual > Forecast → USD แข็ง → ทองอ่อน | "
        "Actual < Forecast → USD อ่อน → ทองแข็ง*",
    ]
    return "\n".join(lines)


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
    """รัน fetch_economic_calendar (FF JSON) และ fetch_gold_news (Perplexity) พร้อมกัน"""
    results = {"calendar": "", "news": ""}
    errors = []

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {
            executor.submit(fetch_economic_calendar): "calendar",   # ไม่ต้องใช้ api_key
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
