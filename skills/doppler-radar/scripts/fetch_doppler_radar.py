import urllib.request
import json
import datetime
import os
import sys

INBOX_DIR = "./digital_twin/Inbox/"

def fetch_polymarket_events():
    url = "https://gamma-api.polymarket.com/markets?limit=50&active=true&closed=false"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return data
    except Exception as e:
        print(f"Error fetching Polymarket data: {e}")
        return None

def process_radar_data(events):
    filtered_events = []
    if not events:
        return filtered_events
    for event in events:
        try:
            volume = float(event.get('volume', 0))
            if volume < 1000000:
                continue
            tokens = event.get('tokens', [])
            if not tokens or len(tokens) < 2:
                continue
            yes_price = float(tokens[0].get('price', 0))
            end_date_str = event.get('endDate')
            if end_date_str:
                end_date = datetime.datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
                days_to_end = (end_date - datetime.datetime.now(datetime.timezone.utc)).days
                if days_to_end > 30:
                    continue
            filtered_events.append({
                'title': event.get('question'),
                'probability': yes_price,
                'volume': volume,
                'days_to_end': days_to_end if end_date_str else 'N/A'
            })
        except Exception:
            continue
    return filtered_events

def main():
    print("Fetching Doppler Radar Data (Polymarket)...")
    events = fetch_polymarket_events()
    high_impact_events = process_radar_data(events)
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_path = os.path.join(INBOX_DIR, f"doppler_radar_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
    
    markdown_content = f"# 多普勒雷达专员 观测报告 (v2.0)\n**生成时间**: {now}\n**数据源**: Polymarket Gamma API\n\n## 叙事溢价补偿 (Narrative Premium) 扫描结果\n\n根据 L3 过滤规则 (TVL > 1M, 结算期 < 30天)：\n"
    
    if not high_impact_events:
        markdown_content += "\n*当前雷达屏幕平静，未扫描到高能近端叙事逼近。*\n"
    else:
        for ev in high_impact_events:
            markdown_content += f"\n### 📡 {ev['title']}\n"
            markdown_content += f"- **当前发生概率 (Yes)**: {ev['probability'] * 100:.1f}%\n"
            markdown_content += f"- **交易量 (Volume)**: ${ev['volume']:,.2f}\n"
            markdown_content += f"- **距结算天数**: {ev['days_to_end']} 天\n"
            markdown_content += "> **评估指令**: 请系统预报中心研判该事件属于宏观利好(I>0)还是利空(I<0)，并计算叙事溢价 ΔE_narrative。\n"

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    print(f"Report generated: {file_path}")

if __name__ == "__main__":
    main()
