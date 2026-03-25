import { useNavigate } from "react-router-dom";
import SecretaryPanel from "../components/SecretaryPanel";
import ThemeToggle from "../components/ThemeToggle";
import type { AgentType } from "../api";

interface Props {
  agent: AgentType;
  title: string;
  icon: string;
  accentColor: string;
}

export default function AgentPage({ agent, title, icon, accentColor }: Props) {
  const navigate = useNavigate();

  return (
    <div className="agent-page">
      <div className="agent-page-header">
        <button className="btn-back" onClick={() => navigate("/")}>
          ← กลับหน้าหลัก
        </button>
        <ThemeToggle />
      </div>

      <SecretaryPanel
        agent={agent}
        title={title}
        icon={icon}
        accentColor={accentColor}
      />
    </div>
  );
}
