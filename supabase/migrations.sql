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

-- knowledge_base: เก็บ Gold Trading Knowledge Base แบ่งตาม Section
create table if not exists knowledge_base (
  id              uuid primary key default gen_random_uuid(),
  part_number     int not null,
  part_name       text not null,
  section_number  text not null,
  section_title   text not null,
  content         text not null,
  topic_tags      text[] not null default '{}',
  created_at      timestamptz not null default now()
);

create index if not exists idx_kb_part on knowledge_base (part_number);
create index if not exists idx_kb_tags on knowledge_base using gin (topic_tags);
create index if not exists idx_kb_section on knowledge_base (section_number);
