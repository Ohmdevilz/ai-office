import type { AgentType } from "../api";

export interface QuickPrompt {
  label: string;
  text: string;
}

export const QUICK_PROMPTS: Record<AgentType, QuickPrompt[]> = {
  marketing: [
    {
      label: "วิเคราะห์คู่แข่ง",
      text: "วิเคราะห์ความเคลื่อนไหวของไปรษณีย์ไทย, Flash Express, KEX Express (Kerry เดิม), J&T Express, Best Express และ Nim Express ในรอบ 7 วันที่ผ่านมา",
    },
    {
      label: "ไอเดีย LINE Broadcast",
      text: "ขอไอเดียสำหรับ Broadcast ใน LINE Official ของ TP Logistics เดือนนี้ซัก 2-3 เรื่อง",
    },
  ],
  trader: [
    {
      label: "วิเคราะห์ทองคำ",
      text: "วิเคราะห์สถานการณ์ตลาดทองคำตอนนี้ M1 M5 M15 H1 เป็นเทรนด์อะไร ขาขึ้น ขาลง หรือ Sideway มี Demand Zone, Supply Zone ตรงไหน จุดเม่าหรือ Liquidity Pool อยู่ตรงไหน เกิด BoS CHoCH ตรงไหน ควรมองหน้า Buy หรือ Sell พร้อมบอกจุดเข้า Entry/SL/TP",
    },
    {
      label: "ข่าวกล่องแดงสัปดาห์นี้",
      text: "ข่าว High Impact ใน Economic Calendar (ในไทยเรียกข่าวกล่องแดงตามตาราง) สัปดาห์นี้มีอะไรบ้าง สถิติเป็นยังไง รอบนี้คาดการณ์ยังไง (ตัวเลขคาดการณ์จะบอกว่าตลาดมองข่าวนี้ว่าจะพาทองไปตรงไหน) จะส่งผลต่อทองคำอย่างไร",
    },
  ],
};
