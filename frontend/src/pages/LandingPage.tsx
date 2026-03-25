import { useNavigate } from "react-router-dom";
import ThemeToggle from "../components/ThemeToggle";

const CARDS = [
  {
    path: "/marketing",
    icon: "📊",
    title: "Marketing Advisor",
    subtitle: "ที่ปรึกษา Marketing ครบวงจร",
    tags: ["Branding", "Content", "Digital", "Strategy"],
    accent: "#3b82f6",
    glow: "rgba(59,130,246,0.15)",
  },
  {
    path: "/trader",
    icon: "📈",
    title: "SMC Trading Analyst",
    subtitle: "นักวิเคราะห์กราฟสาย Smart Money Concept",
    tags: ["Entry / Exit", "FVG", "Order Block", "Demand & Supply"],
    accent: "#10b981",
    glow: "rgba(16,185,129,0.15)",
  },
];

export default function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="landing">
      <div className="page-topbar">
        <ThemeToggle />
      </div>
      <div className="landing-hero">
        <h1 className="landing-title">AI Office</h1>
        <p className="landing-subtitle">เลือกที่ปรึกษา AI ของคุณ</p>
      </div>

      <div className="landing-cards">
        {CARDS.map((card) => (
          <button
            key={card.path}
            className="agent-card"
            style={
              {
                "--card-accent": card.accent,
                "--card-glow": card.glow,
              } as React.CSSProperties
            }
            onClick={() => navigate(card.path)}
          >
            <span className="agent-card-icon">{card.icon}</span>
            <h2 className="agent-card-title">{card.title}</h2>
            <p className="agent-card-subtitle">{card.subtitle}</p>
            <div className="agent-card-tags">
              {card.tags.map((tag) => (
                <span key={tag} className="tag">
                  {tag}
                </span>
              ))}
            </div>
            <span className="agent-card-cta">เริ่มใช้งาน →</span>
          </button>
        ))}
      </div>
    </div>
  );
}
