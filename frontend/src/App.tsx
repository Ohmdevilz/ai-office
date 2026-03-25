import SecretaryPanel from "./components/SecretaryPanel";

export default function App() {
  return (
    <div className="app">
      <header className="app-header">
        <h1>AI Office</h1>
        <p className="app-subtitle">ระบบเลขา AI สำหรับ Marketing &amp; Trading</p>
      </header>

      <main className="panels">
        <SecretaryPanel
          agent="marketing"
          title="Marketing Secretary"
          icon="📊"
          placeholder={'เช่น "คู่แข่งประกาศลดราคาส่ง 15% ทั่วประเทศ TP ควรรับมืออย่างไร?"'}
          accentColor="#3b82f6"
        />

        <SecretaryPanel
          agent="trader"
          title="Trader Secretary"
          icon="📈"
          placeholder={'เช่น "ทองคำทะลุแนวต้าน ทิ้ง FVG ที่ 2050 ควรรอเข้าออเดอร์ที่ไหน?"'}
          accentColor="#10b981"
        />
      </main>
    </div>
  );
}
