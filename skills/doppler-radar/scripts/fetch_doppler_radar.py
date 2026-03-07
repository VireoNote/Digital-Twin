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

def fetch_polymarket_markets():
    """
    抓取 Polymarket 按 24 小时交易量排序的活跃 Markets
    """
    # Fetch top 100 to ensure we have enough after filtering out sports
    url = "https://gamma-api.polymarket.com/markets?limit=100&active=true&closed=false&order=volume24hr&ascending=false"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Error fetching Polymarket Markets: {e}")
        return []

def process_radar_data(markets):
    filtered_markets = []
    if not markets:
        return filtered_markets
        
    sports_keywords = ['sports', 'nba', 'soccer', 'nfl', 'hockey', 'baseball', 'sport', 'premier league', 'la liga', 'champions league', 'tennis', 'f1']

    for market in markets:
        try:
            # 1. 获取基础信息
            question = market.get('question', 'Unknown Question')
            volume24hr = float(market.get('volume24hr', 0))
            
            # 2. 提取父级 Event 的 Tags 和 Title
            tags = []
            event_title = ""
            events = market.get('events', [])
            if events and len(events) > 0:
                parent_event = events[0]
                event_title = parent_event.get('title', '')
                tags = [t.get('label') for t in parent_event.get('tags', []) if 'label' in t]
            
            # 3. 过滤体育类赛事
            lower_tags = [t.lower() for t in tags]
            # Check tags
            if any(word in lower_tags for word in sports_keywords) or any('sport' in t for t in lower_tags):
                continue
            
            # Also check question/event_title aggressively
            q_lower = question.lower() + " " + event_title.lower()
            sports_phrases = ['nba', 'nfl', 'soccer', 'nhl', 'fifa', 'la liga', 'premier league', ' vs ', ' vs. ', 'fc ', 'champions league', 'tennis', 'f1', 'basketball', 'baseball', 'hockey', 'super bowl', 'world cup', 'mlb', ' ufc ', 'mma']
            if any(phrase in q_lower for phrase in sports_phrases):
                continue

            # 4. 解析最高概率
            outcomes = json.loads(market.get('outcomes', '[]'))
            prices = json.loads(market.get('outcomePrices', '[]'))
            
            highest_prob = 0.0
            top_outcome_name = ""
            
            for i, p_str in enumerate(prices):
                p = float(p_str)
                if p > highest_prob:
                    highest_prob = p
                    top_outcome_name = outcomes[i] if i < len(outcomes) else "Unknown"

            # format the question appropriately (if it's a Yes/No market)
            if len(outcomes) == 2 and "Yes" in outcomes and "No" in outcomes:
                display_outcome = f"{top_outcome_name} ({question})"
            else:
                display_outcome = f"{top_outcome_name}"
            
            filtered_markets.append({
                'title': event_title if event_title else question,
                'question': question,
                'volume24hr': volume24hr,
                'top_outcome': display_outcome,
                'highest_prob': highest_prob,
                'tags': tags[:3]
            })
            
        except Exception as e:
            continue
            
    # 只取过滤后的前 50 个
    return filtered_markets[:50]

def main():
    print("Fetching Doppler Radar Data (Polymarket Markets Endpoint)...")
    markets = fetch_polymarket_markets()
    high_impact_markets = process_radar_data(markets)
    
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    target_dir = get_inbox_dir()
    file_path = os.path.join(target_dir, f"doppler_radar_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
    
    markdown_content = f"""# 多普勒雷达专员 观测报告 (v2.3 高频流动性版)
**生成时间**: {now}
**数据源**: Polymarket Gamma API (/markets?order=volume24hr)

## 叙事溢价补偿 (Narrative Premium) 扫描结果
**过滤规则**: 提取全网 24 小时交易量最大的前 50 个独立预测市场 (已过滤体育赛事)。

"""
    
    if not high_impact_markets:
        markdown_content += "\n*当前雷达屏幕平静，未扫描到符合条件的叙事。*\n"
    else:
        for idx, m in enumerate(high_impact_markets, 1):
            tags_str = ", ".join(m['tags'])
            markdown_content += f"\n### 📡 {idx}. {m['question']}\n"
            markdown_content += f"- **24H 资金流转 (Volume 24h)**: ${m['volume24hr']:,.2f}\n"
            markdown_content += f"- **板块标签**: [{tags_str}]\n"
            markdown_content += f"- **当前最热押注 (Top Outcome)**: {m['top_outcome']}\n"
            markdown_content += f"- **隐含发生概率**: {m['highest_prob'] * 100:.1f}%\n"

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    print(f"Report generated: {file_path}")

if __name__ == "__main__":
    main()
