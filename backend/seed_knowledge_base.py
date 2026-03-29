"""
seed_knowledge_base.py
อ่านไฟล์ Gold_Trading_Knowledge_Base.md แล้ว parse แต่ละ section
แล้ว insert เข้า Supabase table: knowledge_base
"""
import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = "https://lwzkwaudoefhbdefmmhe.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

KB_FILE = Path(__file__).parent.parent / "Gold_Trading_Knowledge_Base.md"

# keyword tags ต่อ section เพื่อช่วย search
SECTION_TAGS: dict[str, list[str]] = {
    "1.1": ["ทองไทย", "Gold Spot", "XAU/USD", "session", "เวลาตลาด", "london", "new york", "tokyo"],
    "1.2": ["lot", "leverage", "spread", "pip", "จุด", "mini lot", "micro lot", "standard lot"],
    "1.3": ["TP", "SL", "take profit", "stop loss", "manual close", "trailing", "break even"],
    "1.4": ["candlestick", "แท่งเทียน", "bullish", "bearish", "engulfing", "pin bar", "doji", "rejection"],
    "2.1": ["DXY", "dollar", "ดอลลาร์", "negative correlation", "USD"],
    "2.2": ["FED", "FOMC", "rate", "ดอกเบี้ย", "real yield", "treasury", "dot plot", "jackson hole"],
    "2.3": ["CPI", "NFP", "GDP", "PCE", "ISM", "PMI", "ข่าว", "non-farm payrolls"],
    "2.4": ["Forex Factory", "calendar", "ปฏิทินข่าว", "forecast", "actual", "buy the rumor"],
    "3.1": ["multi-asset", "inter-market", "asset class", "equities", "bonds", "crypto"],
    "3.2": ["correlation", "VIX", "S&P 500", "oil", "WTI", "JPY", "treasury yield", "bitcoin"],
    "3.3": ["risk-on", "risk-off", "safe haven", "ความกลัว", "fear"],
    "3.4": ["margin call", "forced sell", "liquidation", "leverage", "forced buying"],
    "3.5": ["central bank", "de-dollarization", "BRIC", "ธนาคารกลาง", "gold reserve"],
    "3.6": ["case study", "ATH", "all-time high", "DeepSeek", "AI", "สงคราม", "war"],
    "4.1": ["smart money", "SMC", "institutional", "hedge fund", "liquidity hunt"],
    "4.2": ["liquidity", "stop hunt", "equal high", "equal low", "BSL", "SSL", "buy side", "sell side"],
    "4.3": ["BOS", "CHoCH", "market structure", "trend", "break of structure", "change of character"],
    "4.4": ["premium", "discount", "fibonacci", "OTE", "equilibrium", "0.5"],
    "4.5": ["liquidity zone", "buy side liquidity", "sell side liquidity", "inducement"],
    "4.6": ["FVG", "fair value gap", "imbalance", "เต็มช่อง", "3-candle", "void"],
    "4.7": ["order block", "OB", "mitigation", "breaker block", "demand zone", "supply zone"],
    "4.8": ["POI", "confluence", "setup grade", "point of interest", "A+ setup"],
    "5.1": ["OANDA", "position book", "retail sentiment", "long positions", "short positions"],
    "5.2": ["OANDA", "order book", "pending orders", "limit order", "stop order"],
    "5.3": ["framework", "combined analysis", "multi-tool", "confirmation"],
    "6.1": ["liquidity grab", "news trading", "3-step method", "spike", "ข่าวแรง"],
    "6.2": ["multi-timeframe", "MTFA", "D1", "H4", "H1", "M15", "top-down"],
    "6.3": ["entry", "momentum", "correction", "retracement", "continuation", "reversal"],
    "6.4": ["setup grade", "A+ setup", "quality", "checklist", "grade"],
    "7.1": ["lot size", "position size", "คำนวณ lot", "lot calculation", "pip value"],
    "7.2": ["risk per trade", "risk management", "drawdown", "max loss", "1%", "2%"],
    "7.3": ["RR ratio", "risk reward", "1:2", "1:3", "reward", "profit target"],
    "8.1": ["psychology", "mindset", "จิตวิทยา", "emotional", "discipline"],
    "8.2": ["bias", "FOMO", "revenge trade", "overtrading", "confirmation bias", "loss aversion"],
    "8.3": ["trading rules", "กฎการเทรด", "journal", "rules"],
    "8.4": ["SMC framework", "สรุป", "overview", "checklist", "workflow"],
}

PART_RE = re.compile(r"^# PART (\d+): (.+)$")
SECTION_RE = re.compile(r"^## (\d+\.\d+) (.+)$")


def parse_knowledge_base(filepath: Path) -> list[dict]:
    text = filepath.read_text(encoding="utf-8")
    lines = text.splitlines()

    chunks: list[dict] = []
    current_part_num = 0
    current_part_name = ""
    current_section_num = ""
    current_section_title = ""
    current_lines: list[str] = []

    def flush():
        nonlocal current_section_num, current_section_title, current_lines
        if current_section_num and current_lines:
            content = "\n".join(current_lines).strip()
            if content:
                tags = SECTION_TAGS.get(current_section_num, [])
                chunks.append(
                    {
                        "part_number": current_part_num,
                        "part_name": current_part_name,
                        "section_number": current_section_num,
                        "section_title": current_section_title,
                        "content": content,
                        "topic_tags": tags,
                    }
                )
        current_lines = []

    for line in lines:
        part_match = PART_RE.match(line)
        if part_match:
            flush()
            current_part_num = int(part_match.group(1))
            current_part_name = part_match.group(2).strip()
            current_section_num = ""
            current_section_title = ""
            current_lines = []
            continue

        section_match = SECTION_RE.match(line)
        if section_match:
            flush()
            current_section_num = section_match.group(1).strip()
            current_section_title = section_match.group(2).strip()
            current_lines = []
            continue

        if current_section_num:
            current_lines.append(line)

    flush()
    return chunks


def seed():
    if not SUPABASE_KEY:
        print("ERROR: SUPABASE_KEY not set in .env")
        sys.exit(1)

    client = create_client(SUPABASE_URL, SUPABASE_KEY)

    print(f"Parsing {KB_FILE} ...")
    chunks = parse_knowledge_base(KB_FILE)
    print(f"  Parsed {len(chunks)} sections")

    # ลบข้อมูลเก่าออกก่อน (idempotent seed)
    print("Clearing existing knowledge_base rows ...")
    client.table("knowledge_base").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()

    print("Inserting chunks ...")
    # insert ทีละ batch
    batch_size = 10
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        client.table("knowledge_base").insert(batch).execute()
        print(f"  Inserted {min(i + batch_size, len(chunks))}/{len(chunks)}")

    print(f"\nDone! {len(chunks)} sections loaded into knowledge_base.")

    # แสดงสรุป
    for chunk in chunks:
        print(f"  [{chunk['section_number']}] {chunk['section_title'][:50]}")


if __name__ == "__main__":
    seed()
