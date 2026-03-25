import { BrowserRouter, Routes, Route } from "react-router-dom";
import LandingPage from "./pages/LandingPage";
import AgentPage from "./pages/AgentPage";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />

        <Route
          path="/marketing"
          element={
            <AgentPage
              agent="marketing"
              title="Marketing Advisor"
              icon="📊"
              placeholder={'เช่น "อยากทำ Content สำหรับแบรนด์สินค้าใหม่ กลุ่มเป้าหมายอายุ 25-35 ควรเริ่มอย่างไร?"'}
              accentColor="#3b82f6"
            />
          }
        />

        <Route
          path="/trader"
          element={
            <AgentPage
              agent="trader"
              title="SMC Trading Analyst"
              icon="📈"
              placeholder={'เช่น "ทองคำทะลุแนวต้าน ทิ้ง FVG ที่ 2050 ควรรอเข้าออเดอร์ที่ไหน?"'}
              accentColor="#10b981"
            />
          }
        />
      </Routes>
    </BrowserRouter>
  );
}
