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
      label: "วิเคราะห์กราฟทองคำจากรูป",
      text: "วิเคราะห์กราฟทองคำจากรูปที่แนบ บอกว่าเป็นเทรนด์อะไร ขาขึ้น ขาลง หรือ Sideway มี Demand Zone, Supply Zone ตรงไหน จุดเม่าหรือ Liquidity Pool อยู่ตรงไหน เกิด BoS หรือ CHoCH ตรงไหน ควรมองหน้า Buy หรือ Sell พร้อมระบุจุดเข้า Entry, SL และ TP",
    },
    {
      label: "วิเคราะห์ข่าวกล่องแดงจากรูป",
      text: "ข่าว High Impact ใน Economic Calendar (ในไทยเรียกข่าวกล่องแดงตามตาราง) สัปดาห์นี้มีตามรูปที่แนบ วิเคราะห์ให้หน่อยว่าแต่ละข่าวคืออะไร สถิติและ Previous เป็นอย่างไร รอบนี้ตลาดคาดการณ์ว่าจะออกมาในทิศทางไหน (Forecast บอกว่าตลาดมองข่าวนี้ว่าจะพาทองไปทางไหน) และแต่ละข่าวจะส่งผลต่อราคาทองคำอย่างไร",
    },
    {
      label: "ข่าวทองคำวันนี้",
      text: "สรุปข่าวสำคัญที่เกิดขึ้นในรอบ 24 ชั่วโมงที่ผ่านมาที่ส่งผลต่อราคาทองคำ เช่น ข่าว Geopolitical, คำพูดของ Trump หรือเจ้าหน้าที่ Fed นอกตาราง, ความเคลื่อนไหวของตลาดหุ้นและดอลลาร์ และวิเคราะห์ว่าข่าวเหล่านี้ส่งผลต่อทิศทางทองคำอย่างไร",
    },
  ],
};
