import urllib.request
import json
import datetime
import os

INBOX_DIR = "./digital_twin/Inbox/"

def fetch_defillama_stablecoins():
    url = "https://stablecoins.llama.fi/stablecoins"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            total_mcap = 0
            # 遍历所有稳定币，累加其当前的 peggedUSD 流通量
            for asset in data.get('peggedAssets', []):
                circulating = asset.get('circulating', {}).get('peggedUSD', 0)
                total_mcap += circulating
            return total_mcap
    except Exception as e:
        print(f"Error fetching DefiLlama data: {e}")
        return None

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
    
    # 1. 获取稳定币流动性
    total_stablecoin_mcap = fetch_defillama_stablecoins()
    
    # 2. 获取传统金融衍生品与现货 ETF 数据
    cme_price, cme_volume = fetch_yahoo_data("BTC=F")
    ibit_price, ibit_volume = fetch_yahoo_data("IBIT")
    fbtc_price, fbtc_volume = fetch_yahoo_data("FBTC")
    
    if total_stablecoin_mcap is None or cme_price is None or ibit_price is None:
        print("Failed to fetch critical crypto micro data.")
        return

    mcap_billions = total_stablecoin_mcap / 1_000_000_000
    
    # --- L3 Ontology 逻辑分析 ---
    
    # 稳定币购买力分析
    stablecoin_status = "🟡 【水位观察】当前全网稳定币流通总市值约 {:.2f} 十亿美元。请结合当前链上 DeFi (Aave 等) 收益率判定其是否沉淀为‘死水’。".format(mcap_billions)
    
    # ETF vs CME (散户 vs 机构) 背离状态推演
    # 简化判断逻辑：比较 ETF 活跃度与 CME 期货溢价。此处主要以提取基础数据供 LLM 发散推演为主。
    cme_premium = cme_price - (ibit_price * 1000) # IBIT 并非绝对 1:1, 此处作宏观参照
    
    etf_cme_status = "📊 机构(CME)报价: ${:,.2f} | 散户指标(IBIT): ${:,.2f}。如观察到 ETF 大量申购(狂热)，但 CME 未平仓无明显增长甚至存在贴水，需警惕缺乏华尔街长线资金支撑的‘散户逼空’！".format(cme_price, ibit_price)

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_name = f"crypto_micro_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    file_path = os.path.join(INBOX_DIR, file_name)

    markdown_content = f"""# 稳定币流速监控器 (Crypto Micro) 观测报告

**生成时间**: {now}
**数据源**: DefiLlama (Stablecoins), Yahoo Finance (CME, ETFs)

## 核心指标
- **全网稳定币总市值**: {mcap_billions:,.2f} 十亿美元
- **CME 比特币主力期货 (BTC=F)**: ${cme_price:,.2f}
- **贝莱德现货 ETF (IBIT)**: ${ibit_price:,.2f} (单日交易量估值: {ibit_volume:,})
- **富达现货 ETF (FBTC)**: ${fbtc_price:,.2f}

## 交叉验证逻辑 (L3 Ontology Rule)

### 1. 稳定币购买力结构
* {stablecoin_status}

### 2. 资金属性辨别 (散户 vs 机构)
* {etf_cme_status}
"""

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    print(f"Report generated successfully: {file_path}")
    print("Execution complete.")

if __name__ == "__main__":
    main()
