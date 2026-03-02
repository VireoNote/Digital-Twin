import urllib.request
import json
import datetime
import os
import sys

# 将 shared 目录加入路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../Scripts')))
from shared.bayes_macro import load_macro_state, save_macro_state, calculate_ema

API_KEY = "YOUR_FRED_API_KEY_HERE"
INBOX_DIR = "./digital_twin/Inbox/"

def fetch_fred_data(series_id):
    url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={API_KEY}&file_type=json&sort_order=desc&limit=1"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            if 'observations' in data and len(data['observations']) > 0:
                obs = data['observations'][0]
                return float(obs['value']), obs['date']
            return None, None
    except Exception as e:
        print(f"Error fetching {series_id}: {e}")
        return None, None

def main():
    print("Fetching Liquidity Plumbing Data (v1.1)...")
    walcl_val, _ = fetch_fred_data("WALCL")
    tga_val, _ = fetch_fred_data("WTREGEN")
    rrp_val, _ = fetch_fred_data("RRPONTSYD")

    if walcl_val is None or tga_val is None or rrp_val is None:
        print("Failed to fetch.")
        return

    walcl_b = walcl_val / 1000
    tga_b = tga_val / 1000
    rrp_b = rrp_val / 1000
    current_net_liquidity = walcl_b - tga_b - rrp_b

    # --- v1.1 EMA 贝叶斯更新 ---
    state = load_macro_state()
    prev_ema_liq = state.get('net_liquidity_ema', None)
    new_ema_liq = calculate_ema(current_net_liquidity, prev_ema_liq)
    
    state['net_liquidity_current'] = current_net_liquidity
    state['net_liquidity_ema'] = new_ema_liq
    state['last_updated'] = datetime.datetime.now().isoformat()
    save_macro_state(state)

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_path = os.path.join(INBOX_DIR, f"liquidity_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md")

    markdown_content = f"""# 流动性降水专员 观测报告 (v1.1)
**生成时间**: {now}
## 核心指标
- **当前净流动性 (Net Liquidity)**: {current_net_liquidity:,.2f} 十亿美元
- **净流动性 EMA (30天平滑)**: {new_ema_liq:,.2f} 十亿美元 (此值用于计算 E_macro 底色)
- **RRP 余额**: {rrp_b:,.2f} 十亿美元
"""
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    print(f"Report generated: {file_path}")

if __name__ == "__main__":
    main()
