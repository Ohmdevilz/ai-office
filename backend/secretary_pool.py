import os
from crewai import Agent, Task, Crew, Process, LLM
from dotenv import load_dotenv

load_dotenv()

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


def run_trader_task(task_description: str, expected_output: str = "รายงานวิเคราะห์พร้อมแผนการเทรดที่ชัดเจน") -> str:
    llm = _build_llm()
    agent = Agent(
        role="นักวิเคราะห์กราฟและที่ปรึกษาการเทรดสาย SMC",
        goal=(
            "วิเคราะห์กราฟและให้คำปรึกษาการเทรดตามแนวคิด Smart Money Concept (SMC) "
            "ระบุจุด Entry/Exit, โซน Demand/Supply, FVG และ Order Block ได้อย่างแม่นยำ "
            "รวมถึงอธิบายแนวคิดให้มือใหม่เข้าใจได้"
        ),
        backstory=(
            "คุณคือนักวิเคราะห์กราฟสาย SMC ที่เชี่ยวชาญการอ่านพฤติกรรมของ Smart Money "
            "สามารถระบุโซน Demand, Supply, Fair Value Gap (FVG) และ Order Block ได้แม่นยำ "
            "วิเคราะห์จุด Entry/Exit พร้อม Stop Loss และ Take Profit ได้อย่างเป็นระบบ "
            "และสามารถถ่ายทอดความรู้ให้มือใหม่เข้าใจได้ง่าย "
            "ตอบในรูปแบบรายงานวิเคราะห์ที่ชัดเจน มีโครงสร้าง นำไปใช้ได้จริง "
            f"{NO_GREETING}"
        ),
        verbose=True,
        allow_delegation=False,
        llm=llm,
    )
    task = Task(description=task_description, expected_output=expected_output, agent=agent)
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential)
    return str(crew.kickoff())
