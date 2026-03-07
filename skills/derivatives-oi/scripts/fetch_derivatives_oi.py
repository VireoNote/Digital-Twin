import urllib.request
import json
import datetime
import os
import time
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../Scripts')))
from shared.bayes_macro import load_macro_state, calculate_e_macro

BINANCE_API_KEY = "YOUR_BINANCE_API_KEY_HERE"
INBOX_DIR = "./digital_twin/Inbox/"

def fetch_binance_data():
    price_url = "https://fapi.binance.com/fapi/v1/ticker/24hr?symbol=BTCUSDT"
    oi_url = "https://fapi.binance.com/fapi/v1/openInterest?symbol=BTCUSDT"
    try:
        req_price = urllib.request.Request(price_url, headers={'X-MBX-APIKEY': BINANCE_API_KEY})
        with urllib.request.urlopen(req_price) as response:
            btc_price = float(json.loads(response.read().decode())['lastPrice'])

        req_oi = urllib.request.Request(oi_url, headers={'X-MBX-APIKEY': BINANCE_API_KEY})
        with urllib.request.urlopen(req_oi) as response:
            btc_oi = float(json.loads(response.read().decode())['openInterest'])
            
        notional_oi = btc_price * btc_oi
        return btc_price, btc_oi, notional_oi
    except Exception as e:
        print(f"Error fetching Binance data: {e}")
        return None, None, None

def fetch_deribit_dvol():
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
        print(f"Error fetching Deribit DVOL: {e}")
        return None

def main():
    print("Fetching Crypto Extreme Weather Data (v1.1)...")
    
    btc_price, btc_oi, notional_oi = fetch_binance_data()
    btc_dvol = fetch_deribit_dvol()

    if btc_price is None or btc_dvol is None:
        print("Failed to fetch critical data.")
        return

    # --- v1.1 动态阈值缩放 ---
    state = load_macro_state()
    net_liq_ema = state.get('net_liquidity_ema', None)
    tips_ema = state.get('tips_ema', None)
    e_macro = calculate_e_macro(net_liq_ema, tips_ema)
    
    # 基础阈值设定
    base_oi_threshold = 5000000000 # $5B
    base_iv_threshold = 45.0
    
    # 动态缩放 (宏观越宽松，容忍的OI泡沫越高；IV要求越低才报警)
    beta_oi = 1000000000 # 宏观每变动1，OI阈值变动 $1B
    beta_iv = 5.0        # 宏观每变动1，IV报警阈值变动 5
    
    dynamic_oi_threshold = base_oi_threshold + (beta_oi * e_macro)
    dynamic_iv_threshold = base_iv_threshold - (beta_iv * e_macro)

    oi_is_high = notional_oi > dynamic_oi_threshold
    iv_is_low = btc_dvol < dynamic_iv_threshold
    
    if oi_is_high and iv_is_low:
        status_alert = "🔴 【极度高危】动态阈值击穿！当前宏观底色不足以支撑如此高的微观杠杆与极低的保护！"
    elif oi_is_high and not iv_is_low:
        status_alert = "🟡 【警告】杠杆偏高，但尚在宏观环境允许及当前波动率的缓冲范围内。"
    else:
        status_alert = "🟢 【安全】未出现波动率倒挂弹簧结构。"

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_path = os.path.join(INBOX_DIR, f"crypto_weather_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
    notional_oi_b = notional_oi / 1000000000
    dynamic_oi_b = dynamic_oi_threshold / 1000000000

    markdown_content = f"""# 衍生品多空监控器 观测报告 (v1.1 贝叶斯升级版)
**生成时间**: {now}

## 宏观底色修正参数
- **当前宏观系数 (E_macro)**: {e_macro:.2f} [-1(极度紧缩) 到 1(极度宽松)]
- **动态 OI 报警阈值**: {dynamic_oi_b:.2f} 十亿美元 (基准: 5.0)
- **动态 IV 报警阈值**: {dynamic_iv_threshold:.2f} (基准: 45.0)

## 核心指标与触发判定
- **名义 OI 价值**: {notional_oi_b:,.2f} 十亿美元
- **隐含波动率 (DVOL)**: {btc_dvol}
- **判定结果**: {status_alert}
"""
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    print(f"Report generated: {file_path}")

if __name__ == "__main__":
    main()
