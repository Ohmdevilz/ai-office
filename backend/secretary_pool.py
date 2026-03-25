import os
from crewai import Agent, Task, Crew, Process, LLM
from dotenv import load_dotenv

load_dotenv()

# === 1. โหลด API Key จาก .env ===
my_api_key = os.getenv("GEMINI_API_KEY")
if not my_api_key:
    raise ValueError("GEMINI_API_KEY not found. Please set it in the .env file.")

os.environ["GOOGLE_API_KEY"] = my_api_key

# สร้างสมองด้วยคลาส LLM ของ CrewAI โดยตรง (สังเกตคำนำหน้า gemini/)
gemini_llm = LLM(
    model="gemini/gemini-2.5-flash",
    api_key=my_api_key
)

# === 2. สร้างเลขา 2 ตำแหน่ง ===
marketing_sec = Agent(
    role='Marketing Executive Secretary',
    goal='สรุปความเคลื่อนไหวของคู่แข่งในตลาด Bulky จากข่าวสาร',
    backstory='คุณคือเลขาของ Head of Marketing ที่ TP Logistics วิเคราะห์คู่แข่งเก่งมาก',
    verbose=True,
    allow_delegation=False,
    llm=gemini_llm  # ใช้สมองตัวใหม่
)

trader_sec = Agent(
    role='Trader Personal Secretary',
    goal='สรุปภาพรวมราคาและเตรียมข้อมูลกราฟให้ Trader',
    backstory='คุณคือเลขาคู่ใจของ Trader สาย SMC เชี่ยวชาญการสแกนหาจุดเข้าออเดอร์ตามโซน Demand, Supply และ FVG (Fair Value Gap) ในตลาด',
    verbose=True,
    allow_delegation=False,
    llm=gemini_llm  # ใช้สมองตัวใหม่
)

# === 3. มอบหมายงาน (ทดสอบด้วยข้อมูลสมมติก่อน) ===
task_mkt = Task(
    description='ข้อมูลสมมติ: "คู่แข่งรายใหญ่ประกาศลดราคาส่งของชิ้นใหญ่ 15% ทั่วประเทศในสัปดาห์นี้" จงสรุปสั้นๆ 2 บรรทัดว่า TP ควรรับมืออย่างไร',
    expected_output='คำแนะนำสั้นๆ 2 ข้อ',
    agent=marketing_sec
)

task_trade = Task(
    description='ข้อมูลสมมติ: "ทองคำเกิดแท่งเทียนพุ่งแรงทะลุแนวต้าน ทิ้ง FVG ไว้ที่ราคา 2050" จงสรุปให้ Trader ฟังว่าควรรอเข้าออเดอร์ที่ไหน',
    expected_output='แผนการเทรดสั้นๆ',
    agent=trader_sec
)

# === 4. สั่งให้ทำงาน (รวมทีม) ===
office_crew = Crew(
    agents=[marketing_sec, trader_sec],
    tasks=[task_mkt, task_trade],
    process=Process.sequential
)

print("\n🚀 [AI Office] เลขากำลังเริ่มทำงาน...\n")
result = office_crew.kickoff()
print("\n============== รายงานจากเลขา ==============")
print(result)