import urllib.request
import json
import datetime
import os

INBOX_DIR = "./digital_twin/Inbox/" # Relative path for repo
LOCAL_INBOX_DIR = "/home/liwu/digital_twin/Inbox/" # Absolute path for local execution

def get_inbox_dir():
    if os.path.exists("/home/liwu/digital_twin/Inbox/"):
        return LOCAL_INBOX_DIR
    return INBOX_DIR

def fetch_polymarket_events():
    """
    抓取 Polymarket 活跃的宏观 Events (大事件集群)
    """
    url = "https://gamma-api.polymarket.com/events?limit=50&active=true&closed=false"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Error fetching Polymarket Events: {e}")
        return None

def process_radar_data(events):
    filtered_events = []
    if not events:
        return filtered_events
        
    for event in events:
        try:
            # 1. 计算整个 Event 的总交易量
            volume = 0
            if 'volume' in event:
                volume = float(event['volume'])
            elif 'markets' in event and len(event['markets']) > 0:
                volume = sum(float(m.get('volume', 0)) for m in event['markets'])
                
            # 过滤规则: 仅抓取资金量 > 100万美金的大事件
            if volume < 1000000:
                continue

            title = event.get('title', event.get('ticker', 'Unknown Event'))
            
            # 2. 提取该事件下胜率最高的活跃子市场 (Top Outcome)
            top_outcome = "Unknown"
            highest_prob = 0.0
            
            if 'markets' in event and len(event['markets']) > 0:
                for market in event['markets']:
                    if not market.get('active') or market.get('closed'):
                        continue
                    try:
                        prices = json.loads(market.get('outcomePrices', '[]'))
                        outcomes = json.loads(market.get('outcomes', '[]'))
                        if len(prices) > 0 and len(outcomes) > 0:
                            price = float(prices[0])
                            if price > highest_prob:
                                highest_prob = price
                                if outcomes[0].lower() == 'yes':
                                    top_outcome = market.get('question', 'Yes').replace('?', '')
                                else:
                                    top_outcome = outcomes[0]
                    except:
                        pass
            
            # 提取标签，辅助 L3 判断领域
            tags = [t.get('label') for t in event.get('tags', []) if 'label' in t]
            
            filtered_events.append({
                'title': title,
                'volume': volume,
                'top_outcome': top_outcome,
                'highest_prob': highest_prob,
                'tags': tags[:3] # 取前三个主要标签
            })
            
        except Exception as e:
            continue
            
    # 按交易量从大到小排序，只取前 10 个最具影响力的事件
    filtered_events = sorted(filtered_events, key=lambda x: x['volume'], reverse=True)[:10]
    return filtered_events

def main():
    print("Fetching Doppler Radar Data (Polymarket Events Endpoint)...")
    events = fetch_polymarket_events()
    high_impact_events = process_radar_data(events)
    
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    target_dir = get_inbox_dir()
    file_path = os.path.join(target_dir, f"doppler_radar_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
    
    markdown_content = f"""# 多普勒雷达专员 观测报告 (v2.2 宏观全景版)
**生成时间**: {now}
**数据源**: Polymarket Gamma API (/events)

## 叙事溢价补偿 (Narrative Premium) 扫描结果
**过滤规则**: 提取全网交易量 > $1,000,000 的高共识宏观/政治/经济事件，并锁定其中呼声最高的情景。

"""
    
    if not high_impact_events:
        markdown_content += "\n*当前雷达屏幕平静，未扫描到大资金驱动的叙事。*\n"
    else:
        for ev in high_impact_events:
            tags_str = ", ".join(ev['tags'])
            markdown_content += f"\n### 📡 {ev['title']}\n"
            markdown_content += f"- **资金深度 (Volume)**: ${ev['volume']:,.2f}\n"
            markdown_content += f"- **板块标签**: [{tags_str}]\n"
            markdown_content += f"- **当前最热押注 (Top Outcome)**: {ev['top_outcome']}\n"
            markdown_content += f"- **隐含发生概率**: {ev['highest_prob'] * 100:.1f}%\n"
            markdown_content += "> **评估指令**: 请系统预报中心研判该预期结果是否会对加密货币或美元流动性产生宏观利好(I>0)或利空(I<0)，并计入叙事溢价。\n"

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    print(f"Report generated: {file_path}")

if __name__ == "__main__":
    main()
