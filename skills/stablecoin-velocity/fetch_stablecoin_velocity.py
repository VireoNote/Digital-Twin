import urllib.request
import json
import datetime
import os

INBOX_DIR = "/home/liwu/digital_twin/Inbox/"

def fetch_defillama_stablecoins():
    """获取稳定币总流通市值"""
    url = "https://stablecoins.llama.fi/stablecoins"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            total_mcap = 0
            for asset in data.get('peggedAssets', []):
                circulating = asset.get('circulating', {}).get('peggedUSD', 0)
                total_mcap += circulating
            return total_mcap
    except Exception as e:
        print(f"Error fetching Stablecoin Mcap: {e}")
        return None

import math

def fetch_defillama_dex_volume_history():
    """获取过去 14 天的 DEX 交易量历史数据用于计算 Z-Score 和增幅"""
    url = "https://api.llama.fi/overview/dexs?excludeTotalDataChart=false&excludeTotalDataChartBreakdown=true"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            total_chart = data.get('totalDataChart', [])
            if not total_chart or len(total_chart) < 14:
                return []
            # 返回最近 14 天的交易量数据 [timestamp, volume]
            return [float(item[1]) for item in total_chart[-14:]]
    except Exception as e:
        print(f"Error fetching DEX Volume History: {e}")
        return []

def calculate_volume_metrics(vol_history):
    if not vol_history or len(vol_history) < 2:
        return 0, 0, 0
    
    current_vol = vol_history[-1]
    
    # 1. 相对增幅 (% 变化) - 这里由于接口限制只能取日线，我们对比昨日和7日平均
    vol_yesterday = vol_history[-2]
    daily_pct_change = ((current_vol - vol_yesterday) / vol_yesterday) * 100 if vol_yesterday > 0 else 0
    
    # 2. 计算 Z-Score (使用过去 14 天作为窗口)
    mean_vol = sum(vol_history) / len(vol_history)
    variance = sum([((x - mean_vol) ** 2) for x in vol_history]) / len(vol_history)
    std_dev = math.sqrt(variance)
    
    z_score = (current_vol - mean_vol) / std_dev if std_dev > 0 else 0
    
    return daily_pct_change, z_score, mean_vol

def fetch_yahoo_data(ticker):
    url = f"https://query2.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=1d"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            meta = data["chart"]["result"][0]["meta"]
            price = meta.get("regularMarketPrice", 0)
            
            volume = 0
            if "indicators" in data["chart"]["result"][0] and "quote" in data["chart"]["result"][0]["indicators"]:
                quote = data["chart"]["result"][0]["indicators"]["quote"][0]
                if "volume" in quote and quote["volume"] and len(quote["volume"]) > 0:
                    volume = quote["volume"][-1]
            return price, volume
    except Exception as e:
        print(f"Error fetching {ticker} from Yahoo: {e}")
        return None, None

def main():
    print("Fetching Crypto Micro Climate Data...")
    
    # 1. 获取稳定币流动性与流速历史
    total_stablecoin_mcap = fetch_defillama_stablecoins()
    dex_vol_history = fetch_defillama_dex_volume_history()
    daily_dex_volume = dex_vol_history[-1] if dex_vol_history else 0
    daily_pct_change, vol_z_score, _ = calculate_volume_metrics(dex_vol_history)
    
    # 2. 获取传统金融衍生品与现货 ETF 数据
    cme_price, cme_volume = fetch_yahoo_data("BTC=F")
    ibit_price, ibit_volume = fetch_yahoo_data("IBIT")
    fbtc_price, fbtc_volume = fetch_yahoo_data("FBTC")
    
    if total_stablecoin_mcap is None or cme_price is None or ibit_price is None or daily_dex_volume == 0:
        print("Failed to fetch critical crypto micro data.")
        return

    mcap_billions = total_stablecoin_mcap / 1_000_000_000
    vol_billions = daily_dex_volume / 1_000_000_000
    velocity = (daily_dex_volume / total_stablecoin_mcap) * 100 if total_stablecoin_mcap > 0 else 0
    
    # --- L3 Ontology 逻辑分析 ---
    
    # 流速状态研判 (结合静态阈值与动态异动)
    velocity_status = ""
    if velocity >= 10.0:
        velocity_status = "🔴 【极度狂热】稳定币流速极高 (>10%)，资金在疯狂换手，类似 2021 年牛市巅峰，极易引发崩盘。"
    elif velocity >= 5.0:
        velocity_status = "🟢 【健康活跃】稳定币流速适中 (5-10%)，场内换手积极，购买力正在实打实地转化为资产。"
    else:
        velocity_status = "🟡 【死水沉淀】稳定币流速偏低 (<5%)，大量资金只是沉淀在协议或交易所吃利息，并未形成有效购买力。"

    # 添加动态增量与 Z-Score 预警
    anomaly_alert = ""
    if vol_z_score > 2.0:
        anomaly_alert = f"\n⚠️ 【统计学异动】今日 DEX 交易量激增 $\\Delta$Vol > $\\mu + 2\\sigma$ (Z-Score={vol_z_score:.2f}, 环比 {daily_pct_change:+.2f}%)，有大量“死水”正在被突然唤醒！"
    elif vol_z_score < -2.0:
        anomaly_alert = f"\n⚠️ 【流动性枯竭】今日 DEX 交易量断崖下跌 (Z-Score={vol_z_score:.2f})，资金陷入极度观望状态。"
    else:
        anomaly_alert = f"\n🟢 【平稳期】交易量未见显著异动，符合近期均值 (Z-Score={vol_z_score:.2f})。"

    stablecoin_insight = f"{velocity_status}{anomaly_alert}\n*(当前总市值: {mcap_billions:,.2f}B, 今日DEX交易量: {vol_billions:,.2f}B, 日流速: {velocity:.2f}%)*"
    
    # ETF vs CME
    etf_cme_status = "📊 机构(CME)报价: ${:,.2f} | 散户指标(IBIT): ${:,.2f}。如观察到 ETF 大量申购(狂热)，但 CME 未平仓无明显增长甚至存在贴水，需警惕缺乏华尔街长线资金支撑的‘散户逼空’！".format(cme_price, ibit_price)

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_name = f"crypto_micro_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    file_path = os.path.join(INBOX_DIR, file_name)

    markdown_content = f"""# 稳定币流速监控器 (Crypto Micro) 观测报告

**生成时间**: {now}
**数据源**: DefiLlama (Stablecoins & DEX Volume), Yahoo Finance (CME, ETFs)

## 核心指标
- **全网稳定币日流速 (Velocity)**: {velocity:.2f}%
- **今日 DEX 交易量**: ${vol_billions:,.2f} 十亿美元
- **交易量环比变化 (vs昨日)**: {daily_pct_change:+.2f}%
- **交易量 Z-Score (14日均线)**: {vol_z_score:+.2f}
- **全网稳定币总市值**: ${mcap_billions:,.2f} 十亿美元
- **CME 比特币主力期货 (BTC=F)**: ${cme_price:,.2f}
- **贝莱德现货 ETF (IBIT)**: ${ibit_price:,.2f} (单日交易量: {ibit_volume:,})

## 交叉验证逻辑 (L3 Ontology Rule)

### 1. 稳定币真实购买力 (流速 Velocity)
* {stablecoin_insight}

### 2. 资金属性辨别 (散户 vs 机构)
* {etf_cme_status}
"""

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    print(f"Report generated successfully: {file_path}")

if __name__ == "__main__":
    main()