import { useNavigate } from "react-router-dom";
import SecretaryPanel from "../components/SecretaryPanel";
import type { AgentType } from "../api";

interface Props {
  agent: AgentType;
  title: string;
  icon: string;
  placeholder: string;
  accentColor: string;
}

export default function AgentPage({ agent, title, icon, placeholder, accentColor }: Props) {
  const navigate = useNavigate();

  return (
    <div className="agent-page">
      <div className="agent-page-header">
        <button className="btn-back" onClick={() => navigate("/")}>
          ← กลับหน้าหลัก
        </button>
      </div>

      <SecretaryPanel
        agent={agent}
        title={title}
        icon={icon}
        placeholder={placeholder}
        accentColor={accentColor}
      />
    </div>
  );
}
