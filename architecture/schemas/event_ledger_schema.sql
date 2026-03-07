-- L2.3 Event Ledger (事件归并表) Schema
-- 替代复杂的证据图谱，用强类型关系表实现“事件去重”与“特征防重叠”。

CREATE TABLE IF NOT EXISTS event_ledger (
    event_id TEXT PRIMARY KEY,          -- 唯一事件ID (如 hash)
    canonical_event_name TEXT NOT NULL, -- 规范化事件归属 (如 "Fed_Rate_Cut_2026")
    overlap_group TEXT NOT NULL,        -- 去重组标识 (同组事件在进入策略模型时将被降权/合并)
    source TEXT NOT NULL,               -- 数据来源 (如 Polymarket, Binance, OpenNews)
    projection_type TEXT NOT NULL,      -- 投影类型 (Sentiment, Price_Action, Market_Pricing)
    signal_direction INTEGER NOT NULL,  -- 1 (多), 0 (平), -1 (空)
    confidence REAL NOT NULL,           -- 该条事件本身的置信度
    observed_at INTEGER NOT NULL,       -- 探测到的时间戳
    effective_at INTEGER NOT NULL,      -- 逻辑生效时间戳
    dedupe_key TEXT UNIQUE NOT NULL     -- 用于物理防重的 Hash (source + canonical_event_name + timestamp_hour)
);

CREATE INDEX IF NOT EXISTS idx_overlap_group ON event_ledger(overlap_group);
CREATE INDEX IF NOT EXISTS idx_observed_at ON event_ledger(observed_at);
