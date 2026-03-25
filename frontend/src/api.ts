const BASE_URL = "https://ai-office-production-4bd2.up.railway.app";

export type AgentType = "marketing" | "trader";

export interface TaskRequest {
  task: string;
  expected_output?: string;
}

export interface TaskResponse {
  agent: AgentType;
  result: string;
}

export async function runTask(
  agent: AgentType,
  body: TaskRequest
): Promise<TaskResponse> {
  const res = await fetch(`${BASE_URL}/api/${agent}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? "Unknown error");
  }

  return res.json();
}
