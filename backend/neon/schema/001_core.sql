-- NARIS core backend schema contract
-- Target: Neon / PostgreSQL
-- Apply only through a reviewed migration on an isolated development branch.

create extension if not exists pgcrypto;

create table if not exists naris_player (
    player_id uuid primary key default gen_random_uuid(),
    external_subject text unique,
    display_name text,
    locale text not null default 'en',
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists naris_save_slot (
    save_id uuid primary key default gen_random_uuid(),
    player_id uuid not null references naris_player(player_id) on delete cascade,
    slot_no smallint not null check (slot_no between 1 and 10),
    world_id text not null,
    checkpoint_id text,
    save_version integer not null default 1,
    payload jsonb not null default '{}'::jsonb,
    checksum text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    unique (player_id, slot_no)
);

create table if not exists naris_inventory_item (
    inventory_item_id uuid primary key default gen_random_uuid(),
    player_id uuid not null references naris_player(player_id) on delete cascade,
    asset_id text not null,
    quantity integer not null default 1 check (quantity >= 0),
    state jsonb not null default '{}'::jsonb,
    acquired_at timestamptz not null default now(),
    unique (player_id, asset_id)
);

create table if not exists naris_entitlement (
    entitlement_id uuid primary key default gen_random_uuid(),
    player_id uuid not null references naris_player(player_id) on delete cascade,
    entitlement_key text not null,
    source text not null,
    granted_at timestamptz not null default now(),
    revoked_at timestamptz,
    metadata jsonb not null default '{}'::jsonb,
    unique (player_id, entitlement_key)
);

create table if not exists naris_gameplay_event (
    event_id bigserial primary key,
    player_id uuid references naris_player(player_id) on delete set null,
    session_id uuid,
    event_name text not null,
    world_id text,
    build_version text,
    occurred_at timestamptz not null default now(),
    properties jsonb not null default '{}'::jsonb
);

create index if not exists idx_naris_save_player on naris_save_slot(player_id);
create index if not exists idx_naris_inventory_player on naris_inventory_item(player_id);
create index if not exists idx_naris_event_player_time on naris_gameplay_event(player_id, occurred_at desc);
create index if not exists idx_naris_event_name_time on naris_gameplay_event(event_name, occurred_at desc);
