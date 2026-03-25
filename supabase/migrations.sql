-- conversations: เก็บประวัติการสนทนาของ agent ทั้ง marketing และ trader
create table if not exists conversations (
  id          uuid primary key default gen_random_uuid(),
  agent       text not null check (agent in ('marketing', 'trader')),
  task        text not null,
  expected_output text,
  result      text not null,
  created_at  timestamptz not null default now()
);

-- index สำหรับ query ตาม agent + เรียงตาม created_at
create index if not exists idx_conversations_agent_created
  on conversations (agent, created_at desc);
