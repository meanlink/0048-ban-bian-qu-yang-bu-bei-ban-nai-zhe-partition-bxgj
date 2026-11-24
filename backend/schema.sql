CREATE TABLE IF NOT EXISTS board_lots(
 code text PRIMARY KEY,label text NOT NULL,panel_mm int NOT NULL CHECK(panel_mm>0),
 max_deflection numeric(5,2) NOT NULL CHECK(max_deflection>0),
 max_spread numeric(5,2) NOT NULL CHECK(max_spread>0)
);
CREATE TABLE IF NOT EXISTS flex_fixtures(
 code text PRIMARY KEY,label text NOT NULL,span_mm int NOT NULL CHECK(span_mm>0),
 panel_mm int NOT NULL CHECK(panel_mm>0),cal_due date NOT NULL,offset_mm numeric(4,2) NOT NULL
);
CREATE TABLE IF NOT EXISTS backing_samples(
 code text PRIMARY KEY,lot text NOT NULL REFERENCES board_lots(code),
 zone text NOT NULL CHECK(zone IN ('bound','heart')),sheet text NOT NULL,
 UNIQUE(lot,zone,sheet)
);
CREATE TABLE IF NOT EXISTS flex_cards(
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 sample text NOT NULL REFERENCES backing_samples(code), fixture text NOT NULL REFERENCES flex_fixtures(code),
 observed_on date NOT NULL, deflection numeric(5,2) NOT NULL CHECK(deflection>=0),
 normalized numeric(5,2) NOT NULL, stage text NOT NULL DEFAULT 'active' CHECK(stage IN ('active','excluded')),
 exclusion text, CHECK((stage='active')=(exclusion IS NULL))
);
CREATE UNIQUE INDEX IF NOT EXISTS active_flex_card ON flex_cards(sample) WHERE stage='active';
CREATE TABLE IF NOT EXISTS frame_cut_orders(
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 lot text NOT NULL REFERENCES board_lots(code),
 kept_width int NOT NULL CHECK(kept_width>0),
 issuer text NOT NULL REFERENCES app_users(email),
 inspection jsonb NOT NULL,
 request_key text NOT NULL,
 status text NOT NULL DEFAULT 'active' CHECK(status IN ('active','voided')),
 void_reason text,
 voided_at timestamptz,
 voided_by text REFERENCES app_users(email),
 created_at timestamptz NOT NULL DEFAULT now(),
 job bigint UNIQUE NOT NULL REFERENCES app_jobs(id),
 CHECK((status='active')=(void_reason IS NULL)),
 CHECK((status='active')=(voided_at IS NULL)),
 CHECK((status='active')=(voided_by IS NULL))
);
CREATE UNIQUE INDEX IF NOT EXISTS frame_cut_request ON frame_cut_orders(lot,request_key);
CREATE UNIQUE INDEX IF NOT EXISTS frame_cut_active_lot ON frame_cut_orders(lot) WHERE status='active';
CREATE INDEX IF NOT EXISTS frame_cut_lot_history ON frame_cut_orders(lot,created_at);
