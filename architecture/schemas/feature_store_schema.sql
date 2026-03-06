-- L2.2 Feature Store (时序特征库) Schema 
-- 建议使用 SQLite 或 DuckDB 运行

-- 核心设计原则：严格时序对齐，使用大宽表或星型模型管理慢变量和快变量

-- 1. 慢变量表 (Macro Slow Variables)
-- 更新频率：日更/周更
CREATE TABLE IF NOT EXISTS macro_base_features (
    timestamp_utc INTEGER PRIMARY KEY, -- Unix Timestamp (精确到日)
    date_str TEXT NOT NULL,          -- YYYY-MM-DD 方便人类阅读
    walcl_billions REAL,             -- 美联储总资产 (WALCL)
    tga_billions REAL,               -- 财政部一般账户 (TGA)
    rrp_billions REAL,               -- 隔夜逆回购 (RRP)
    net_liquidity_billions REAL,     -- 净流动性计算值
    dxy_index REAL,                  -- 美元指数
    tips_yield REAL,                 -- 实际利率
    t10y2y_spread REAL,              -- 收益率曲线倒挂深度
    e_macro_base REAL                -- 聚合的宏观底色系数 [-1, 1]
);

-- 2. 预期变量表 (Expectation Variables)
-- 更新频率：日更/小时更
CREATE TABLE IF NOT EXISTS narrative_premium_features (
    timestamp_utc INTEGER PRIMARY KEY,
    date_str TEXT NOT NULL,
    polymarket_fed_cut_prob REAL,    -- Polymarket 降息押注概率 (主线)
    polymarket_election_prob REAL,   -- 关键大选押注概率
    nlp_sentiment_alpha REAL,        -- L2.1 输出的体感情绪连续因子 [-1, 1]
    e_narrative_offset REAL          -- 综合叙事溢价补偿值
);

-- 3. 快变量表 (Micro Fast Variables)
-- 更新频率：小时更/甚至分钟更
CREATE TABLE IF NOT EXISTS micro_trigger_features (
    timestamp_utc INTEGER PRIMARY KEY, -- Unix Timestamp (精确到小时/分钟)
    datetime_str TEXT NOT NULL,      -- YYYY-MM-DD HH:MM:SS
    asset_symbol TEXT NOT NULL,      -- 标的资产 (如 BTC, ETH)
    price_usd REAL,                  -- 当前价格
    oi_coin_margined REAL,           -- 币本位未平仓合约量 (用于剔除价格噪音)
    oi_usd_value REAL,               -- U本位名义价值 (用于算杠杆率天花板)
    funding_rate REAL,               -- 资金费率
    dvol_index REAL,                 -- 隐含波动率 (保护垫)
    stablecoin_total_mcap REAL,      -- 全网稳定币总市值
    dex_daily_volume REAL,           -- DEX 24H 真实换手量
    stablecoin_velocity REAL,        -- 流速 (Velocity = Volume / Mcap)
    oi_z_score_14d REAL,             -- 动态计算的 OI 偏离度
    velocity_z_score_14d REAL        -- 动态计算的流速偏离度
);

-- 建立索引加速范围查询与时序对齐 (AS OF JOIN)
CREATE INDEX IF NOT EXISTS idx_micro_asset ON micro_trigger_features(asset_symbol);