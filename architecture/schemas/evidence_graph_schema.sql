-- L2.3 Evidence Graph (证据图谱) Schema
-- 采用 SQLite 关系型表模拟轻量级图数据库结构
-- 核心目标：消除多重共线性，实现“实体消歧”与“单一事件汇聚”

-- 1. 实体表 (Entity Node) - 图的顶点
-- 代表宏观或微观中不可再分的“客观事实实体”，如“降息预期”、“局部爆仓踩踏”
CREATE TABLE IF NOT EXISTS entities (
    entity_id TEXT PRIMARY KEY,       -- UUID 或 哈希标识
    entity_name TEXT NOT NULL,        -- 如 "Fed_Rate_Cut_2026", "BTC_Short_Squeeze"
    entity_type TEXT NOT NULL,        -- MACRO_EVENT, MICRO_STATE, NARRATIVE
    created_at INTEGER NOT NULL,      -- 首次探测到的时间戳
    status TEXT DEFAULT 'ACTIVE'      -- ACTIVE, RESOLVED, INVALIDATED
);

-- 2. 证据源表 (Evidence Source) - 产生噪音和投影的源头
-- 区分是谁产生了这条“主观或客观证据”
CREATE TABLE IF NOT EXISTS sources (
    source_id TEXT PRIMARY KEY,
    source_type TEXT NOT NULL,        -- POLYMARKET, OPENNEWS_MCP, BINANCE_API, FRED
    reliability_weight REAL DEFAULT 1.0 -- 该数据源在系统中的基础置信度
);

-- 3. 证据投影边表 (Evidence Edges) - 将各个感官的切片连线至单一实体
-- 这是防止“重复计价”的核心所在
CREATE TABLE IF NOT EXISTS evidence_edges (
    edge_id TEXT PRIMARY KEY,
    entity_id TEXT NOT NULL,          -- 锚定的目标底层实体
    source_id TEXT NOT NULL,          -- 证据的提供者
    timestamp_utc INTEGER NOT NULL,   -- 该证据捕获的时间戳
    
    -- 证据携带的属性
    signal_direction INTEGER,         -- 1 (支持实体发生), -1 (反对), 0 (中性)
    signal_strength REAL,             -- 该证据的强度 (如概率、Z-Score 绝对值)
    raw_content TEXT,                 -- 原始证据载体 (如某条新闻的 URL/标题，或某项指标的 JSON 截图)
    
    FOREIGN KEY(entity_id) REFERENCES entities(entity_id),
    FOREIGN KEY(source_id) REFERENCES sources(source_id)
);

-- 建立索引，方便系统在执行贝叶斯推断前，按实体聚合 (GROUP BY entity_id) 所有去重证据
CREATE INDEX IF NOT EXISTS idx_edge_entity ON evidence_edges(entity_id);
CREATE INDEX IF NOT EXISTS idx_edge_timestamp ON evidence_edges(timestamp_utc);