import { useState } from "react";
import { runTask } from "../api";
import type { AgentType } from "../api";
import FormatSelector from "./FormatSelector";
import QuickPrompts from "./QuickPrompts";
import { FORMAT_OPTIONS } from "../data/formats";
import { QUICK_PROMPTS } from "../data/quickPrompts";

interface Props {
  agent: AgentType;
  title: string;
  icon: string;
  accentColor: string;
}

type Status = "idle" | "loading" | "success" | "error";

export default function SecretaryPanel({ agent, title, icon, accentColor }: Props) {
  const [task, setTask] = useState("");
  const [selectedFormat, setSelectedFormat] = useState("");
  const [result, setResult] = useState("");
  const [status, setStatus] = useState<Status>("idle");
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!task.trim()) return;

    setStatus("loading");
    setError("");
    setResult("");

    try {
      const res = await runTask(agent, {
        task: task.trim(),
        ...(selectedFormat && { expected_output: selectedFormat }),
      });
      setResult(res.result);
      setStatus("success");
    } catch (err) {
      setError(err instanceof Error ? err.message : "เกิดข้อผิดพลาด");
      setStatus("error");
    }
  }

  function handleClear() {
    setTask("");
    setSelectedFormat("");
    setResult("");
    setError("");
    setStatus("idle");
  }

  const isLoading = status === "loading";

  return (
    <div className="panel" style={{ "--accent": accentColor } as React.CSSProperties}>
      <div className="panel-header">
        <span className="panel-icon">{icon}</span>
        <h2>{title}</h2>
      </div>

      <form onSubmit={handleSubmit} className="panel-form">
        <QuickPrompts
          prompts={QUICK_PROMPTS[agent]}
          onSelect={(text) => setTask(text)}
          disabled={isLoading}
        />

        <label>
          คำสั่ง / โจทย์
          <textarea
            value={task}
            onChange={(e) => setTask(e.target.value)}
            rows={4}
            disabled={isLoading}
          />
          <span className="input-hint">
            ใส่คำสั่งหรือโจทย์ที่ต้องการ แล้วเลือกรูปแบบผลลัพธ์ด้านล่าง จากนั้นกด ส่งคำสั่ง
          </span>
        </label>

        <div className="format-section">
          <span className="format-label">
            รูปแบบผลลัพธ์ <span className="optional">(optional)</span>
          </span>
          <FormatSelector
            options={FORMAT_OPTIONS[agent]}
            selected={selectedFormat}
            onChange={setSelectedFormat}
            disabled={isLoading}
          />
        </div>

        <div className="panel-actions">
          <button
            type="submit"
            className="btn-primary"
            disabled={isLoading || !task.trim()}
          >
            {isLoading ? (
              <><span className="spinner" /> กำลังประมวลผล…</>
            ) : (
              "ส่งคำสั่ง"
            )}
          </button>

          {status !== "idle" && (
            <button type="button" className="btn-ghost" onClick={handleClear}>
              ล้าง
            </button>
          )}
        </div>
      </form>

      {status === "error" && (
        <div className="result-box result-error">
          <strong>เกิดข้อผิดพลาด</strong>
          <p>{error}</p>
        </div>
      )}

      {status === "success" && (
        <div className="result-box result-success">
          <div className="result-header">
            <span>ผลลัพธ์</span>
            <button className="btn-copy" onClick={() => navigator.clipboard.writeText(result)}>
              คัดลอก
            </button>
          </div>
          <pre className="result-text">{result}</pre>
        </div>
      )}
    </div>
  );
}
