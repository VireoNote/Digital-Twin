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

def fetch_fred_series(series_id, limit=2):
    url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={API_KEY}&file_type=json&sort_order=desc&limit={limit}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            if 'observations' in data and len(data['observations']) >= limit:
                return [float(obs['value']) for obs in data['observations'] if obs['value'] != '.']
            return None
    except Exception as e:
        print(f"Error fetching {series_id}: {e}")
        return None

def main():
    print("Fetching Policy Pressure Data (v1.1)...")
    
    tips_data = fetch_fred_series("DFII10")  # 10-Year TIPS
    usd_data = fetch_fred_series("DTWEXBGS") # Broad Dollar Index
    t10y2y_data = fetch_fred_series("T10Y2Y") # Yield Curve
    
    if not all([tips_data, usd_data, t10y2y_data]):
        print("Failed to fetch.")
        return

    tips_current = tips_data[0]

    # --- v1.1 EMA 贝叶斯更新 ---
    state = load_macro_state()
    prev_ema_tips = state.get('tips_ema', None)
    new_ema_tips = calculate_ema(tips_current, prev_ema_tips)
    
    state['tips_current'] = tips_current
    state['tips_ema'] = new_ema_tips
    state['last_updated'] = datetime.datetime.now().isoformat()
    save_macro_state(state)

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_path = os.path.join(INBOX_DIR, f"policy_pressure_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md")

    markdown_content = f"""# 宏观收益率特征提取器 观测报告 (v1.1)
**生成时间**: {now}
## 核心指标
- **当前 TIPS 收益率**: {tips_current}%
- **TIPS EMA (30天平滑)**: {new_ema_tips}% (此值用于计算 E_macro 底色)
- **T10Y2Y**: {t10y2y_data[0]}%
"""
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    print(f"Report generated: {file_path}")

if __name__ == "__main__":
    main()
