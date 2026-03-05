import urllib.request
import json
import datetime
import os
import time
import math
import sys

INBOX_DIR = "/home/liwu/digital_twin/Inbox/"

def fetch_binance_oi_hist():
    """获取过去 24 小时的 OI 历史数据 (1H K线)"""
    url = "https://fapi.binance.com/futures/data/openInterestHist?symbol=BTCUSDT&period=1h&limit=25"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return data
    except Exception as e:
        print(f"Error fetching historical OI: {e}")
        return []

def fetch_binance_ticker_and_funding():
    """获取 24H 价格变化及当前资金费率"""
    ticker_url = "https://fapi.binance.com/fapi/v1/ticker/24hr?symbol=BTCUSDT"
    funding_url = "https://fapi.binance.com/fapi/v1/premiumIndex?symbol=BTCUSDT"
    try:
        req_ticker = urllib.request.Request(ticker_url)
        with urllib.request.urlopen(req_ticker) as response:
            ticker_data = json.loads(response.read().decode())
            price = float(ticker_data['lastPrice'])
            price_change = float(ticker_data['priceChangePercent'])

        req_funding = urllib.request.Request(funding_url)
        with urllib.request.urlopen(req_funding) as response:
            funding_data = json.loads(response.read().decode())
            funding_rate = float(funding_data['lastFundingRate'])

        return price, price_change, funding_rate
    except Exception as e:
        print(f"Error fetching ticker/funding: {e}")
        return None, None, None

def fetch_deribit_dvol():
    """获取隐含波动率，用于判断保护垫"""
    current_time = int(time.time() * 1000)
    start_time = current_time - (86400 * 1000)
    url = f"https://www.deribit.com/api/v2/public/get_volatility_index_data?currency=BTC&resolution=1D&start_timestamp={start_time}&end_timestamp={current_time}"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            if 'result' in data and 'data' in data['result'] and len(data['result']['data']) > 0:
                return float(data['result']['data'][-1][4])
            return None
    except Exception as e:
        return None

def calculate_z_score(oi_list):
    """计算滚动时间窗口的 OI Z-Score"""
    if not oi_list or len(oi_list) < 2:
        return 0, 0, 0
    values = [float(x['sumOpenInterest']) for x in oi_list]
    mean = sum(values) / len(values)
    variance = sum([((x - mean) ** 2) for x in values]) / len(values)
    std_dev = math.sqrt(variance)
    current = values[-1]
    if std_dev == 0:
        return 0, mean, std_dev
    z_score = (current - mean) / std_dev
    return z_score, mean, std_dev

def main():
    print("Fetching Crypto Extreme Weather Data (v2.0 Dynamic Increment)...")
    
    price, price_change, funding_rate = fetch_binance_ticker_and_funding()
    oi_hist = fetch_binance_oi_hist()
    dvol = fetch_deribit_dvol()

    if price is None or not oi_hist:
        print("Failed to fetch critical data.")
        return

    current_oi_data = oi_hist[-1]
    current_oi_value = float(current_oi_data['sumOpenInterestValue']) # 用于计算杠杆率 (U本位)
    current_oi_coin = float(current_oi_data['sumOpenInterest'])       # 用于计算真实增量 (币本位)
    cmc_supply = float(current_oi_data.get('CMCCirculatingSupply', 19600000))
    
    # 1. 杠杆率警告（OI / Market Cap）- 必须使用同计价单位(U本位)
    market_cap = price * cmc_supply
    leverage_ratio = (current_oi_value / market_cap) * 100 if market_cap > 0 else 0

    # 2. 突发性相对增幅 (% 变化) - 严格使用币本位剔除价格噪音
    oi_1h_ago_coin = float(oi_hist[-2]['sumOpenInterest']) if len(oi_hist) >= 2 else current_oi_coin
    oi_4h_ago_coin = float(oi_hist[-5]['sumOpenInterest']) if len(oi_hist) >= 5 else current_oi_coin
    
    delta_oi_1h_pct = ((current_oi_coin - oi_1h_ago_coin) / oi_1h_ago_coin) * 100 if oi_1h_ago_coin > 0 else 0
    delta_oi_4h_pct = ((current_oi_coin - oi_4h_ago_coin) / oi_4h_ago_coin) * 100 if oi_4h_ago_coin > 0 else 0

    # 3. 标准差偏离度 (Z-Score)
    z_score, mean_oi, std_oi = calculate_z_score(oi_hist)

    # 4. 判断多空状态模型 (结合 Delta Price, Delta OI, Funding Rate)
    price_direction = 1 if price_change > 0 else -1 
    oi_direction = 1 if delta_oi_4h_pct > 0 else -1

    market_state = "震荡整理"
    if price_direction > 0 and oi_direction > 0 and funding_rate > 0:
        market_state = "🚀 **多头建仓 (Long Build-up)**: OI 显著增加，价格上涨，资金费率为正。这是健康上涨趋势的标志，说明多头资金实打实在入场。"
    elif price_direction > 0 and oi_direction < 0 and funding_rate <= 0:
        market_state = "🔥 **空头回补/爆仓 (Short Covering)**: OI 显著减少，价格上涨，资金费率偏负。说明这波上涨是由空头认输止损推动的，缺乏真正的多头新资金支撑。"
    elif price_direction < 0 and oi_direction > 0 and funding_rate < 0:
        market_state = "🩸 **空头建仓 (Short Build-up)**: OI 显著增加，价格下跌，资金费率为负。空头主导市场下杀，大量做空资金入场。"
    elif price_direction < 0 and oi_direction < 0 and funding_rate > 0:
        market_state = "💥 **多头平仓/踩踏 (Long Liquidation)**: OI 显著减少，价格下跌，资金费率偏正。多头恐慌出逃，发生了明显的去杠杆和爆仓。"
    else:
        market_state = "⚖️ **多空分歧 (Mixed Signals)**: 动能杂乱，没有形成绝对共识。"

    # 评估显著性警告
    alerts = []
    if leverage_ratio > 2.5:
        alerts.append(f"🔴 【杠杆过热】全网 OI / 流通市值比例达到 {leverage_ratio:.2f}% (临界点 >2.5%)，市场充斥着高杠杆，随时可能发生剧烈去杠杆（上下插针）。")
    else:
        alerts.append(f"🟢 【杠杆健康】全网 OI / 流通市值比例为 {leverage_ratio:.2f}% (低位安全区)，OI的稳步上升具备扎实的现货支撑。")

    if delta_oi_1h_pct >= 5.0 or delta_oi_4h_pct >= 5.0:
        alerts.append(f"🔴 【突发性激增】OI 在短时间内出现剧烈爆发 (1H: {delta_oi_1h_pct:+.2f}%, 4H: {delta_oi_4h_pct:+.2f}%)。若超 10% 极大可能伴随暴力洗盘！")
    elif delta_oi_1h_pct <= -5.0 or delta_oi_4h_pct <= -5.0:
        alerts.append(f"🟡 【大规模平仓】OI 短期出现大幅滑落 (4H: {delta_oi_4h_pct:+.2f}%)，正在进行急烈的去杠杆。")
        
    if z_score > 2.0:
        alerts.append(f"🔴 【统计学极值】当前 OI 增量 $\\Delta$OI > $\\mu + 2\\sigma$ (Z-Score = {z_score:.2f})！说明资金流入具备极高的统计学异动意义。")
    elif z_score < -2.0:
        alerts.append(f"🔴 【统计学极值】当前 OI 大幅低于均线 $- 2\\sigma$ (Z-Score = {z_score:.2f})，发生严重踩踏。")

    if not any("🔴" in a for a in alerts) and not any("🟡" in a for a in alerts):
        alerts.append("🟢 当前相对基准与历史波动均无显著异动。")

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_path = os.path.join(INBOX_DIR, f"crypto_weather_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
    
    alerts_str = "\n".join([f"- {a}" for a in alerts])
    
    markdown_content = f"""# 加密雷暴预警专员 观测报告 (v2.0 动态增量与行为归因版)
**生成时间**: {now}

## 核心指标
- **当前价格 (BTC)**: ${price:,.2f} (24H: {price_change:+.2f}%)
- **资金费率 (Funding Rate)**: {funding_rate*100:.4f}%
- **隐含波动率 (DVOL)**: {dvol if dvol else 'N/A'}
- **全网名义未平仓量 (OI)**: ${current_oi_value/1e9:,.2f} B

## 动态增量与杠杆率评估
- **OI 1H 变化率**: {delta_oi_1h_pct:+.2f}%
- **OI 4H 变化率**: {delta_oi_4h_pct:+.2f}%
- **标准差偏离度 (Z-Score)**: {z_score:+.2f}
- **杠杆率 (OI / Market Cap)**: {leverage_ratio:.2f}%

## 市场资金行为推演 (Probability Model)
**当前资金面状态**: {market_state}

## 异动预警雷达
{alerts_str}
"""
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    print(f"Report generated: {file_path}")

if __name__ == "__main__":
    main()
