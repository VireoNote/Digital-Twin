#!/usr/bin/env python3
import urllib.request
import json
import os
import sys
from datetime import datetime

# API Token (User provided for opennews-mcp)
TOKEN = os.environ.get("OPENNEWS_TOKEN", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiNmhURnJSaThBTW8yQ2pwYnJhUjFrRlM4eWRXS1ZUajl5eFV1NmZjWGdxVkUiLCJub25jZSI6IjkzNDE2ZTAxLTIwMTUtNDJjNy1iNTBiLTRkMzUwZDQ3ZTlhYiIsImlhdCI6MTc3MjczOTkwMSwianRpIjoiZDJkZDIzNTctNzQ1MC00OGZlLThhYjQtMzkwYTkxOTI0ZGI0In0.vaiHB2vaqxzFaL8lu6uR0_Q2Mr4S6d46Azp4VEMXIWw")

def fetch_news(query=""):
    url = "https://ai.6551.io/open/news_search"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "q": query,
        "limit": 50,
        "page": 1
    }
    
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data.get("data", [])
    except Exception as e:
        print(f"Error fetching news: {e}", file=sys.stderr)
        return []

def calculate_alpha(news_items):
    if not news_items:
        return 0.0, 0, 0, 0
    
    total_score = 0
    bullish_count = 0
    bearish_count = 0
    neutral_count = 0
    valid_items = 0
    
    for item in news_items:
        ai_rating = item.get("aiRating", {})
        score = ai_rating.get("score", 0)
        signal = ai_rating.get("signal", "neutral")
        
        if signal == "long":
            total_score += score
            bullish_count += 1
            valid_items += 1
        elif signal == "short":
            total_score -= score
            bearish_count += 1
            valid_items += 1
        else:
            neutral_count += 1
            
    if valid_items == 0:
        return 0.0, bullish_count, bearish_count, neutral_count
        
    alpha_factor = total_score / (valid_items * 100) # Normalize to [-1, 1] range based on score severity
    return alpha_factor, bullish_count, bearish_count, neutral_count

def generate_report(alpha_factor, bullish, bearish, neutral, top_news):
    now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    report = f"""# 体感温度情绪监控报告 (NLP Sentiment Alpha)
生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 情绪指标 (Alpha Factor)
**当前连续 Alpha 因子**: `{alpha_factor:.4f}`  *(取值范围 [-1, 1], >0偏多, <0偏空)*

## 样本分布 (最近50条高权重资讯)
- 🟢 看多 (Long) 样本: {bullish}
- 🔴 看空 (Short) 样本: {bearish}
- ⚪ 中性 (Neutral) 样本: {neutral}

## 核心驱动事件 (Top 3 Signals)
"""
    count = 0
    for item in top_news:
        if count >= 3:
            break
        ai_rating = item.get("aiRating", {})
        if ai_rating.get("signal") in ["long", "short"] and ai_rating.get("score", 0) >= 60:
            signal_emoji = "🟢" if ai_rating.get("signal") == "long" else "🔴"
            report += f"- {signal_emoji} **[{ai_rating.get('score')}分]** {item.get('text', '')[:100]}...\n"
            count += 1
            
    return report, now_str

def main():
    query = sys.argv[1] if len(sys.argv) > 1 else ""
    news = fetch_news(query)
    if not news:
        print("Failed to fetch news or no news available.")
        sys.exit(1)
        
    alpha, bull, bear, neut = calculate_alpha(news)
    report, now_str = generate_report(alpha, bull, bear, neut, news)
    
    # Save to L1 Inbox
    inbox_dir = "/home/liwu/digital_twin/Inbox/"
    os.makedirs(inbox_dir, exist_ok=True)
    filename = os.path.join(inbox_dir, f"sentiment_alpha_{now_str}.md")
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(report)
        
    print(f"Success: Alpha {alpha:.4f}. Report saved to {filename}")
    print("=" * 40)
    print(report)

if __name__ == "__main__":
    main()
