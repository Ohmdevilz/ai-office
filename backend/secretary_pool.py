import os
from crewai import Agent, Task, Crew, Process, LLM
from dotenv import load_dotenv

load_dotenv()


def _build_llm() -> LLM:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found. Please set it in the .env file.")
    return LLM(model="gemini/gemini-2.5-flash", api_key=api_key)


def run_marketing_task(task_description: str, expected_output: str = "คำแนะนำสั้นๆ 2-3 ข้อ") -> str:
    llm = _build_llm()
    agent = Agent(
        role="Marketing Executive Secretary",
        goal="สรุปความเคลื่อนไหวของคู่แข่งในตลาด Bulky จากข่าวสาร",
        backstory="คุณคือเลขาของ Head of Marketing ที่ TP Logistics วิเคราะห์คู่แข่งเก่งมาก ตอบในรูปแบบรายงานสรุปที่วิเคราะห์เป็นเรื่องเป็นราว แต่ห้ามขึ้นต้นด้วยคำว่า 'เรียน...' หรือประโยคเปิดแบบจดหมายทุกรูปแบบ ให้เริ่มด้วยหัวข้อหรือเนื้อหาได้เลย",
        verbose=True,
        allow_delegation=False,
        llm=llm,
    )
    task = Task(description=task_description, expected_output=expected_output, agent=agent)
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential)
    result = crew.kickoff()
    return str(result)


def run_trader_task(task_description: str, expected_output: str = "แผนการเทรดสั้นๆ") -> str:
    llm = _build_llm()
    agent = Agent(
        role="Trader Personal Secretary",
        goal="สรุปภาพรวมราคาและเตรียมข้อมูลกราฟให้ Trader",
        backstory="คุณคือเลขาคู่ใจของ Trader สาย SMC เชี่ยวชาญการสแกนหาจุดเข้าออเดอร์ตามโซน Demand, Supply และ FVG (Fair Value Gap) ในตลาด ตอบในรูปแบบรายงานสรุปที่วิเคราะห์เป็นเรื่องเป็นราว แต่ห้ามขึ้นต้นด้วยคำว่า 'เรียน...' หรือประโยคเปิดแบบจดหมายทุกรูปแบบ ให้เริ่มด้วยหัวข้อหรือเนื้อหาได้เลย",
        verbose=True,
        allow_delegation=False,
        llm=llm,
    )
    task = Task(description=task_description, expected_output=expected_output, agent=agent)
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential)
    result = crew.kickoff()
    return str(result)