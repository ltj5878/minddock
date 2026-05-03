-- MindDock Initial Schema
-- Run this in Supabase SQL Editor

create extension if not exists vector;

-- Users
create table users (
    id uuid primary key default gen_random_uuid(),
    email text unique not null,
    hashed_password text,
    notion_access_token text,
    notion_default_database_id text,
    preferred_llm text default 'openai',
    custom_llm_api_base text,
    custom_llm_api_key text,
    custom_llm_model_name text,
    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

-- Projects
create table projects (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references users(id) on delete cascade,
    notion_project_page_id text,
    name text not null,
    goal text,
    status text default 'active' check (status in ('active', 'paused', 'completed', 'archived')),
    created_at timestamptz default now(),
    updated_at timestamptz default now()
);
create index idx_projects_user on projects(user_id);

-- Notes
create table notes (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references users(id) on delete cascade,
    notion_page_id text,
    title text not null,
    content text not null,
    summary text,
    type text default 'note' check (type in ('note', 'idea', 'reference', 'meeting', 'journal', 'task_note')),
    tags text[] default '{}',
    project_id uuid references projects(id) on delete set null,
    source_url text,
    source_type text check (source_type in ('manual', 'notion_sync', 'zhihu', 'yuque', 'url', 'direct')),
    action_items text[] default '{}',
    created_at timestamptz default now(),
    updated_at timestamptz default now(),
    last_synced_at timestamptz
);
create index idx_notes_user on notes(user_id);
create index idx_notes_project on notes(project_id);
create index idx_notes_type on notes(user_id, type);
create index idx_notes_tags on notes using gin(tags);

-- Embeddings
create table embeddings (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references users(id) on delete cascade,
    note_id uuid not null references notes(id) on delete cascade,
    chunk_index int not null,
    chunk_text text not null,
    embedding vector(1536) not null,
    metadata jsonb default '{}',
    created_at timestamptz default now()
);
create index idx_embeddings_note on embeddings(note_id);
create index idx_embeddings_user on embeddings(user_id);
create index idx_embeddings_vector on embeddings
    using hnsw (embedding vector_cosine_ops)
    with (m = 16, ef_construction = 64);

-- Tasks
create table tasks (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references users(id) on delete cascade,
    notion_task_page_id text,
    title text not null,
    status text default 'todo' check (status in ('todo', 'in_progress', 'done', 'cancelled')),
    priority text default 'medium' check (priority in ('low', 'medium', 'high', 'urgent')),
    due_date date,
    project_id uuid references projects(id) on delete set null,
    source_note_id uuid references notes(id) on delete set null,
    created_at timestamptz default now(),
    updated_at timestamptz default now()
);
create index idx_tasks_user on tasks(user_id);
create index idx_tasks_project on tasks(project_id);
create index idx_tasks_status on tasks(user_id, status);

-- Sync cursors
create table sync_cursors (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references users(id) on delete cascade,
    notion_database_id text not null,
    last_synced_at timestamptz not null,
    cursor_token text,
    unique(user_id, notion_database_id)
);

-- Vector similarity search function
create or replace function match_embeddings(
    query_embedding vector(1536),
    match_user_id uuid,
    match_threshold float default 0.7,
    match_count int default 10
) returns table (
    id uuid,
    note_id uuid,
    chunk_text text,
    metadata jsonb,
    similarity float
) language plpgsql as $$
begin
    return query
    select
        e.id,
        e.note_id,
        e.chunk_text,
        e.metadata,
        1 - (e.embedding <=> query_embedding) as similarity
    from embeddings e
    where e.user_id = match_user_id
      and 1 - (e.embedding <=> query_embedding) > match_threshold
    order by e.embedding <=> query_embedding
    limit match_count;
end;
$$;
