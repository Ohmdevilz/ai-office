import logging
import os
import litellm
from crewai import Agent, Task, Crew, Process, LLM
from dotenv import load_dotenv
from database import search_knowledge_base, format_kb_context
from perplexity_service import fetch_gold_news

load_dotenv()

logger = logging.getLogger(__name__)

NO_GREETING = (
    "ห้ามขึ้นต้นด้วยคำว่า 'เรียน' 'จากภารกิจที่ได้รับ' หรือประโยคเกริ่นนำใดๆ "
    "ให้เริ่มตอบด้วยเนื้อหาได้เลยทันที"
)


def _build_llm() -> LLM:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found. Please set it in the .env file.")
    return LLM(model="gemini/gemini-2.5-flash", api_key=api_key)


def run_marketing_task(task_description: str, expected_output: str = "รายงานสรุปพร้อมคำแนะนำที่นำไปใช้ได้จริง") -> str:
    llm = _build_llm()
    agent = Agent(
        role="ที่ปรึกษา Marketing ครบวงจร",
        goal=(
            "ให้คำปรึกษาและวิเคราะห์ด้าน Marketing ครอบคลุมทุกมิติ "
            "ทั้ง Branding, Content Marketing, Digital Marketing และ Strategy "
            "เพื่อให้ผู้รับสามารถนำไปตัดสินใจและปฏิบัติได้จริง"
        ),
        backstory=(
            "คุณคือที่ปรึกษา Marketing มืออาชีพที่มีประสบการณ์ครอบคลุมทุกด้าน "
            "ตั้งแต่การวาง Brand Strategy, การทำ Content ที่โดนใจกลุ่มเป้าหมาย, "
            "การใช้ช่องทาง Digital อย่างมีประสิทธิภาพ ไปจนถึงการวิเคราะห์คู่แข่งและตลาด "
            "ตอบในรูปแบบรายงานที่วิเคราะห์ชัดเจน นำไปใช้ได้จริง "
            f"{NO_GREETING}"
        ),
        verbose=True,
        allow_delegation=False,
        llm=llm,
    )
    task = Task(description=task_description, expected_output=expected_output, agent=agent)
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential)
    return str(crew.kickoff())


def _analyze_chart_image(image_base64: str, api_key: str) -> str:
    """ใช้ Gemini Vision อ่านกราฟจากรูปภาพ Base64 แล้วคืนคำอธิบายกราฟเป็นข้อความ"""
    response = litellm.completion(
        model="gemini/gemini-2.5-flash",
        api_key=api_key,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                    },
                    {
                        "type": "text",
                        "text": (
                            "วิเคราะห์กราฟนี้ตามหลัก Smart Money Concept (SMC) สำหรับ XAU/USD อย่างละเอียด:\n"
                            "1. ระบุ Timeframe และประเภทกราฟ\n"
                            "2. Market Structure ปัจจุบัน (Bullish/Bearish, BOS/CHoCH ล่าสุด)\n"
                            "3. โซน Order Block ที่เห็นชัดเจน (ระบุราคาโดยประมาณ)\n"
                            "4. Fair Value Gap (FVG) ที่ยังไม่ถูก Fill\n"
                            "5. Liquidity Pools (Equal High/Low, BSL/SSL)\n"
                            "6. Premium/Discount Zone ปัจจุบันราคาอยู่ที่ไหน\n"
                            "7. แนวโน้มและจุดสังเกตสำคัญอื่นๆ\n"
                            "ตอบเป็นภาษาไทย อธิบายสิ่งที่เห็นในกราฟให้ละเอียดที่สุด"
                        ),
                    },
                ],
            }
        ],
    )
    return response.choices[0].message.content or ""


def run_trader_task(
    task_description: str,
    expected_output: str = "รายงานวิเคราะห์พร้อมแผนการเทรดที่ชัดเจน",
    image_base64: str | None = None,
) -> str:
    llm = _build_llm()
    api_key = os.getenv("GOOGLE_API_KEY") or ""
    perplexity_key = os.getenv("PERPLEXITY_API_KEY") or ""

    # 1) ดึง Knowledge Base ที่เกี่ยวข้อง
    kb_chunks = search_knowledge_base(task_description, limit=5)
    kb_context = format_kb_context(kb_chunks)

    # 2) ดึง Gold News ล่าสุดจาก Perplexity
    gold_news_context = ""
    if perplexity_key:
        try:
            raw_news = fetch_gold_news(perplexity_key)
            if raw_news:
                gold_news_context = (
                    "=== GOLD NEWS — ข่าวล่าสุด 24-48 ชม. ===\n"
                    f"{raw_news}\n"
                    "=== END GOLD NEWS ===\n"
                )
        except Exception as exc:
            logger.warning("fetch_gold_news failed: %s", exc)

    # 3) วิเคราะห์รูปกราฟด้วย Gemini Vision (ถ้ามีรูป)
    chart_analysis = ""
    if image_base64 and api_key:
        raw = _analyze_chart_image(image_base64, api_key)
        chart_analysis = (
            "\n=== CHART IMAGE ANALYSIS (Gemini Vision) ===\n"
            f"{raw}\n"
            "=== END CHART ANALYSIS ===\n"
        )

    # รวม context ทั้งหมด: KB + Gold News + Chart + Task
    enriched_task = f"{kb_context}\n{gold_news_context}{chart_analysis}\n{task_description}"

    agent = Agent(
        role="นักวิเคราะห์กราฟและที่ปรึกษาการเทรดสาย SMC",
        goal=(
            "วิเคราะห์กราฟและให้คำปรึกษาการเทรดตามแนวคิด Smart Money Concept (SMC) "
            "โดยอ้างอิง Knowledge Base ที่ให้มาเป็นหลัก "
            "ระบุจุด Entry/Exit, โซน Demand/Supply, FVG และ Order Block ได้อย่างแม่นยำ "
            "รวมถึงอธิบายแนวคิดให้มือใหม่เข้าใจได้"
        ),
        backstory=(
            "คุณคือนักวิเคราะห์กราฟสาย SMC ที่เชี่ยวชาญการอ่านพฤติกรรมของ Smart Money "
            "คุณมีฐานความรู้ครอบคลุมตั้งแต่พื้นฐาน XAU/USD, การวิเคราะห์มหภาค, "
            "กระแสเงินทุนโลก, SMC (Liquidity, FVG, Order Block, BOS/CHoCH), "
            "เครื่องมือ OANDA, เทคนิคการเทรด, Money Management และ Trading Psychology "
            "ก่อนตอบทุกครั้ง คุณจะอ้างอิง Knowledge Base ใน KNOWLEDGE BASE REFERENCE "
            "และ Gold News ล่าสุดใน GOLD NEWS "
            "และถ้ามี CHART IMAGE ANALYSIS ให้อ้างอิงผลวิเคราะห์กราฟนั้นประกอบด้วย "
            "เพื่อให้การวิเคราะห์ครอบคลุมทั้งเทคนิคและปัจจัยมหภาคล่าสุด "
            "ตอบในรูปแบบรายงานวิเคราะห์ที่ชัดเจน มีโครงสร้าง นำไปใช้ได้จริง "
            f"{NO_GREETING}"
        ),
        verbose=True,
        allow_delegation=False,
        llm=llm,
    )
    task = Task(description=enriched_task, expected_output=expected_output, agent=agent)
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential)
    return str(crew.kickoff())
