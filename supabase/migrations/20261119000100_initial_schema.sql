-- ==============================================================================
-- Migration: 20261119000100_initial_schema.sql
-- Project: Smart Farmer Hackathon Platform
-- Target Database: Supabase PostgreSQL 17
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- 0. Helper Functions, Extensions & Auth Automation
-- ------------------------------------------------------------------------------
create extension if not exists "pgcrypto";

-- Generic timestamp updater trigger
create or replace function public.set_current_timestamp_updated_at()
returns trigger
language plpgsql
security invoker
set search_path = ''
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

-- Secure automatic farmer-profile creation on auth.users registration
-- Uses ON CONFLICT DO NOTHING so farmer-customized profile info is preserved
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
begin
  insert into public.profiles (
    id,
    full_name,
    phone,
    preferred_language
  )
  values (
    new.id,
    coalesce(nullif(trim(new.raw_user_meta_data->>'full_name'), ''), 'Farmer'),
    nullif(trim(new.raw_user_meta_data->>'phone'), ''),
    coalesce(nullif(trim(new.raw_user_meta_data->>'preferred_language'), ''), 'en')
  )
  on conflict (id) do nothing;

  return new;
end;
$$;

-- Revoke direct execution privileges from unprivileged roles (defense in depth)
revoke all on function public.handle_new_user() from public, anon, authenticated;

-- Trigger to create initial farmer profile upon Supabase Auth sign-up
drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();

-- ------------------------------------------------------------------------------
-- 1. Profiles (Farmer identity linked 1:1 with auth.users)
-- ------------------------------------------------------------------------------
create table public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  full_name text not null check (char_length(trim(full_name)) > 0),
  phone text check (phone is null or phone ~ '^\+?[0-9]{10,15}$'),
  preferred_language text not null default 'en',
  state text,
  district text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create trigger trg_profiles_updated_at
  before update on public.profiles
  for each row execute function public.set_current_timestamp_updated_at();

-- ------------------------------------------------------------------------------
-- 2. Farms (Supports multiple farms per farmer with coordinates)
-- ------------------------------------------------------------------------------
create table public.farms (
  id uuid primary key default gen_random_uuid(),
  farmer_id uuid not null references public.profiles(id) on delete cascade,
  name text not null check (char_length(trim(name)) > 0),
  location_name text not null,
  latitude numeric(10, 7) not null check (latitude between -90.0 and 90.0),
  longitude numeric(10, 7) not null check (longitude between -180.0 and 180.0),
  total_area_acres numeric(8, 2) check (total_area_acres is null or total_area_acres > 0),
  soil_type text,
  irrigation_type text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index idx_farms_farmer_id on public.farms(farmer_id);
create index idx_farms_location on public.farms(latitude, longitude);

create trigger trg_farms_updated_at
  before update on public.farms
  for each row execute function public.set_current_timestamp_updated_at();

-- ------------------------------------------------------------------------------
-- 3. Crop Catalog (Global reference data for supported crops)
-- ------------------------------------------------------------------------------
create table public.crop_catalog (
  id uuid primary key default gen_random_uuid(),
  name text not null unique check (char_length(trim(name)) > 0),
  scientific_name text,
  category text not null check (category in ('cereal', 'pulse', 'oilseed', 'vegetable', 'fruit', 'cash_crop', 'spice', 'other')),
  season text not null check (season in ('kharif', 'rabi', 'zaid', 'perennial', 'all_season')),
  typical_duration_days integer check (typical_duration_days is null or typical_duration_days > 0),
  description text,
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index idx_crop_catalog_category_season on public.crop_catalog(category, season);

create trigger trg_crop_catalog_updated_at
  before update on public.crop_catalog
  for each row execute function public.set_current_timestamp_updated_at();

-- ------------------------------------------------------------------------------
-- 4. Crop Cycles (Multiple crop cycles per farm)
-- ------------------------------------------------------------------------------
create table public.crop_cycles (
  id uuid primary key default gen_random_uuid(),
  farm_id uuid not null references public.farms(id) on delete cascade,
  crop_id uuid not null references public.crop_catalog(id) on delete restrict,
  variety text,
  sowing_date date not null,
  expected_harvest_date date check (expected_harvest_date is null or expected_harvest_date >= sowing_date),
  actual_harvest_date date check (actual_harvest_date is null or actual_harvest_date >= sowing_date),
  area_acres numeric(8, 2) check (area_acres is null or area_acres > 0),
  current_stage text not null default 'sowing' check (
    current_stage in ('land_prep', 'sowing', 'germination', 'vegetative', 'flowering', 'yield_formation', 'ripening', 'harvested', 'failed', 'cancelled')
  ),
  status text not null default 'active' check (status in ('planned', 'active', 'completed', 'abandoned')),
  notes text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  -- Composite unique constraint to support composite foreign key consistency in child tables
  constraint uk_crop_cycles_id_farm unique (id, farm_id)
);

create index idx_crop_cycles_farm_id on public.crop_cycles(farm_id);
create index idx_crop_cycles_crop_id on public.crop_cycles(crop_id);
create index idx_crop_cycles_stage_status on public.crop_cycles(current_stage, status);

create trigger trg_crop_cycles_updated_at
  before update on public.crop_cycles
  for each row execute function public.set_current_timestamp_updated_at();

-- ------------------------------------------------------------------------------
-- 5. Crop Stage Rules (Configurable JSONB rules for agronomic validation)
-- ------------------------------------------------------------------------------
create table public.crop_stage_rules (
  id uuid primary key default gen_random_uuid(),
  crop_id uuid not null references public.crop_catalog(id) on delete cascade,
  stage_key text not null check (
    stage_key in ('land_prep', 'sowing', 'germination', 'vegetative', 'flowering', 'yield_formation', 'ripening', 'harvested', 'failed', 'cancelled')
  ),
  stage_name text not null check (char_length(trim(stage_name)) > 0),
  stage_order integer not null check (stage_order > 0),
  duration_days_min integer check (duration_days_min is null or duration_days_min >= 0),
  duration_days_max integer check (duration_days_max is null or duration_days_max >= duration_days_min),
  rules jsonb not null default '{}'::jsonb,
  is_verified boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  -- Ensures exactly one stage definition per key and per display order per crop
  constraint uk_crop_stage_key unique (crop_id, stage_key),
  constraint uk_crop_stage_order unique (crop_id, stage_order)
);

create index idx_crop_stage_rules_crop_id on public.crop_stage_rules(crop_id);
create index idx_crop_stage_rules_verified on public.crop_stage_rules(crop_id, is_verified);
create index idx_crop_stage_rules_key on public.crop_stage_rules(crop_id, stage_key);

create trigger trg_crop_stage_rules_updated_at
  before update on public.crop_stage_rules
  for each row execute function public.set_current_timestamp_updated_at();

-- ------------------------------------------------------------------------------
-- 6. Weather Records (Timestamped farm-specific observed weather)
-- ------------------------------------------------------------------------------
create table public.weather_records (
  id uuid primary key default gen_random_uuid(),
  farm_id uuid not null references public.farms(id) on delete cascade,
  observed_at timestamptz not null,
  temperature_celsius numeric(5, 2),
  humidity_pct numeric(5, 2) check (humidity_pct is null or (humidity_pct between 0.0 and 100.0)),
  rainfall_mm numeric(7, 2) check (rainfall_mm is null or rainfall_mm >= 0.0),
  wind_speed_kmh numeric(5, 2) check (wind_speed_kmh is null or wind_speed_kmh >= 0.0),
  solar_radiation_w_m2 numeric(7, 2) check (solar_radiation_w_m2 is null or solar_radiation_w_m2 >= 0.0),
  source text not null default 'weather_station',
  created_at timestamptz not null default now(),
  constraint uk_farm_weather_observation unique (farm_id, observed_at)
);

create index idx_weather_records_farm_observed on public.weather_records(farm_id, observed_at desc);

-- ------------------------------------------------------------------------------
-- 7. Weather Forecasts (Timestamped future forecasts linked to farms)
-- ------------------------------------------------------------------------------
create table public.weather_forecasts (
  id uuid primary key default gen_random_uuid(),
  farm_id uuid not null references public.farms(id) on delete cascade,
  forecast_generated_at timestamptz not null,
  forecast_target_time timestamptz not null check (forecast_target_time >= forecast_generated_at),
  temperature_min_celsius numeric(5, 2),
  temperature_max_celsius numeric(5, 2) check (temperature_max_celsius is null or temperature_min_celsius is null or temperature_max_celsius >= temperature_min_celsius),
  precipitation_probability_pct numeric(5, 2) check (precipitation_probability_pct is null or (precipitation_probability_pct between 0.0 and 100.0)),
  precipitation_mm numeric(7, 2) check (precipitation_mm is null or precipitation_mm >= 0.0),
  weather_condition text,
  forecast_provider text not null default 'open_meteo',
  created_at timestamptz not null default now(),
  -- Protects against duplicate ingestion while preserving distinct forecast revisions
  constraint uk_farm_forecast_revision unique (farm_id, forecast_provider, forecast_generated_at, forecast_target_time)
);

create index idx_weather_forecasts_farm_target on public.weather_forecasts(farm_id, forecast_target_time);

-- ------------------------------------------------------------------------------
-- 8. Market Prices (Mandi commodity prices - global reference data)
-- ------------------------------------------------------------------------------
create table public.market_prices (
  id uuid primary key default gen_random_uuid(),
  crop_id uuid references public.crop_catalog(id) on delete set null,
  commodity_name text not null check (char_length(trim(commodity_name)) > 0),
  variety text,
  state text not null,
  district text not null,
  market_mandi text not null,
  modal_price_per_quintal numeric(10, 2) not null check (modal_price_per_quintal >= 0.0),
  min_price_per_quintal numeric(10, 2) check (min_price_per_quintal is null or min_price_per_quintal >= 0.0),
  max_price_per_quintal numeric(10, 2) check (max_price_per_quintal is null or max_price_per_quintal >= 0.0),
  price_date date not null,
  source text not null default 'agmarknet',
  created_at timestamptz not null default now(),
  -- PostgreSQL 17 NULLS NOT DISTINCT treats NULL varieties as identical across mandi/source/location
  constraint uk_market_prices_unique unique nulls not distinct (
    source, state, district, market_mandi, commodity_name, variety, price_date
  ),
  -- Ensures logical price order: min_price <= modal_price <= max_price
  constraint chk_market_prices_ordering check (
    (min_price_per_quintal is null or min_price_per_quintal <= modal_price_per_quintal)
    and
    (max_price_per_quintal is null or modal_price_per_quintal <= max_price_per_quintal)
  )
);

create index idx_market_prices_lookup on public.market_prices(state, district, market_mandi, commodity_name, price_date desc);
create index idx_market_prices_crop_id on public.market_prices(crop_id);

-- ------------------------------------------------------------------------------
-- 9. Risk Assessments (Explainable agronomic/weather risk assessments)
-- ------------------------------------------------------------------------------
create table public.risk_assessments (
  id uuid primary key default gen_random_uuid(),
  farm_id uuid not null references public.farms(id) on delete cascade,
  crop_cycle_id uuid,
  risk_category text not null check (risk_category in ('pest', 'disease', 'weather_drought', 'weather_flood', 'heat_stress', 'frost', 'market', 'general')),
  risk_level text not null check (risk_level in ('low', 'medium', 'high', 'severe')),
  risk_score numeric(5, 2) check (risk_score is null or (risk_score between 0.0 and 100.0)),
  factors jsonb not null default '{}'::jsonb,
  assessed_at timestamptz not null default now(),
  created_at timestamptz not null default now(),
  -- Composite foreign key enforces strict consistency between farm_id and crop_cycle_id
  constraint fk_risk_assessments_crop_cycle_farm
    foreign key (crop_cycle_id, farm_id)
    references public.crop_cycles(id, farm_id)
    on delete cascade
);

create index idx_risk_assessments_farm_assessed on public.risk_assessments(farm_id, assessed_at desc);
create index idx_risk_assessments_crop_cycle on public.risk_assessments(crop_cycle_id);

-- ------------------------------------------------------------------------------
-- 10. Notifications (User notifications and status tracking)
-- ------------------------------------------------------------------------------
create table public.notifications (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.profiles(id) on delete cascade,
  title text not null check (char_length(trim(title)) > 0),
  message text not null,
  type text not null default 'info' check (type in ('info', 'alert', 'warning', 'reminder', 'risk_alert')),
  status text not null default 'unread' check (status in ('unread', 'read', 'archived', 'dismissed')),
  read_at timestamptz,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index idx_notifications_user_status on public.notifications(user_id, status, created_at desc);

-- Automatically manage read_at on notification status transitions
create or replace function public.handle_notification_status_update()
returns trigger
language plpgsql
security invoker
set search_path = ''
as $$
begin
  if new.status = 'read' and old.status <> 'read' and new.read_at is null then
    new.read_at = now();
  elsif new.status = 'unread' then
    new.read_at = null;
  end if;
  return new;
end;
$$;

create trigger trg_notifications_read_at
  before update on public.notifications
  for each row execute function public.handle_notification_status_update();

-- ------------------------------------------------------------------------------
-- 11. Role Privileges & Grants (Principle of Least Privilege)
-- ------------------------------------------------------------------------------
-- Revoke all default table access from anon and authenticated
revoke all on table
  public.profiles,
  public.farms,
  public.crop_catalog,
  public.crop_cycles,
  public.crop_stage_rules,
  public.weather_records,
  public.weather_forecasts,
  public.market_prices,
  public.risk_assessments,
  public.notifications
from anon, authenticated;

-- Service role retains full administrative access
grant all on table
  public.profiles,
  public.farms,
  public.crop_catalog,
  public.crop_cycles,
  public.crop_stage_rules,
  public.weather_records,
  public.weather_forecasts,
  public.market_prices,
  public.risk_assessments,
  public.notifications
to service_role;

-- Authenticated user granular table grants
grant select, insert, update on public.profiles to authenticated;
grant select, insert, update, delete on public.farms to authenticated;
grant select, insert, update, delete on public.crop_cycles to authenticated;

-- Authenticated notification grants: restricted to select, delete, and updating ONLY the status column
grant select, delete on public.notifications to authenticated;
grant update (status) on public.notifications to authenticated;

-- Authenticated read-only grants for reference and system-generated tables
grant select on public.crop_catalog to authenticated;
grant select on public.crop_stage_rules to authenticated;
grant select on public.market_prices to authenticated;
grant select on public.weather_records to authenticated;
grant select on public.weather_forecasts to authenticated;
grant select on public.risk_assessments to authenticated;

-- ------------------------------------------------------------------------------
-- 12. Row Level Security (RLS) Setup
-- ------------------------------------------------------------------------------
alter table public.profiles enable row level security;
alter table public.farms enable row level security;
alter table public.crop_catalog enable row level security;
alter table public.crop_cycles enable row level security;
alter table public.crop_stage_rules enable row level security;
alter table public.weather_records enable row level security;
alter table public.weather_forecasts enable row level security;
alter table public.market_prices enable row level security;
alter table public.risk_assessments enable row level security;
alter table public.notifications enable row level security;

-- --- Profiles Policies ---
create policy "profiles_select_own" on public.profiles
  for select to authenticated
  using ((select auth.uid()) = id);

create policy "profiles_insert_own" on public.profiles
  for insert to authenticated
  with check ((select auth.uid()) = id);

create policy "profiles_update_own" on public.profiles
  for update to authenticated
  using ((select auth.uid()) = id)
  with check ((select auth.uid()) = id);

-- --- Farms Policies (Supports multiple farms per farmer) ---
create policy "farms_select_own" on public.farms
  for select to authenticated
  using (farmer_id = (select auth.uid()));

create policy "farms_insert_own" on public.farms
  for insert to authenticated
  with check (farmer_id = (select auth.uid()));

create policy "farms_update_own" on public.farms
  for update to authenticated
  using (farmer_id = (select auth.uid()))
  with check (farmer_id = (select auth.uid()));

create policy "farms_delete_own" on public.farms
  for delete to authenticated
  using (farmer_id = (select auth.uid()));

-- --- Crop Catalog Policies (Authenticated read-only for active crops) ---
create policy "crop_catalog_select_active" on public.crop_catalog
  for select to authenticated
  using (is_active = true);

-- --- Crop Cycles Policies (Farmers manage crop cycles for their farms) ---
create policy "crop_cycles_select_own" on public.crop_cycles
  for select to authenticated
  using (
    farm_id in (
      select f.id from public.farms f
      where f.farmer_id = (select auth.uid())
    )
  );

create policy "crop_cycles_insert_own" on public.crop_cycles
  for insert to authenticated
  with check (
    farm_id in (
      select f.id from public.farms f
      where f.farmer_id = (select auth.uid())
    )
  );

create policy "crop_cycles_update_own" on public.crop_cycles
  for update to authenticated
  using (
    farm_id in (
      select f.id from public.farms f
      where f.farmer_id = (select auth.uid())
    )
  )
  with check (
    farm_id in (
      select f.id from public.farms f
      where f.farmer_id = (select auth.uid())
    )
  );

create policy "crop_cycles_delete_own" on public.crop_cycles
  for delete to authenticated
  using (
    farm_id in (
      select f.id from public.farms f
      where f.farmer_id = (select auth.uid())
    )
  );

-- --- Crop Stage Rules Policies (Authenticated read-only for verified rules) ---
create policy "crop_stage_rules_select_verified" on public.crop_stage_rules
  for select to authenticated
  using (is_verified = true);

-- --- Weather Records Policies (Farmers read records for their farms) ---
create policy "weather_records_select_own_farm" on public.weather_records
  for select to authenticated
  using (
    farm_id in (
      select f.id from public.farms f
      where f.farmer_id = (select auth.uid())
    )
  );

-- --- Weather Forecasts Policies (Farmers read forecasts for their farms) ---
create policy "weather_forecasts_select_own_farm" on public.weather_forecasts
  for select to authenticated
  using (
    farm_id in (
      select f.id from public.farms f
      where f.farmer_id = (select auth.uid())
    )
  );

-- --- Market Prices Policies (Authenticated read-only access to mandi prices) ---
create policy "market_prices_select_all" on public.market_prices
  for select to authenticated
  using (true);

-- --- Risk Assessments Policies (Farmers read risk assessments for their farms) ---
create policy "risk_assessments_select_own_farm" on public.risk_assessments
  for select to authenticated
  using (
    farm_id in (
      select f.id from public.farms f
      where f.farmer_id = (select auth.uid())
    )
  );

-- --- Notifications Policies (Farmers view, update status, and manage their own notifications) ---
create policy "notifications_select_own" on public.notifications
  for select to authenticated
  using (user_id = (select auth.uid()));

create policy "notifications_update_own" on public.notifications
  for update to authenticated
  using (user_id = (select auth.uid()))
  with check (user_id = (select auth.uid()));

create policy "notifications_delete_own" on public.notifications
  for delete to authenticated
  using (user_id = (select auth.uid()));
