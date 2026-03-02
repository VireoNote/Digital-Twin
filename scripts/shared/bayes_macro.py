import os
import json
from datetime import datetime

STATE_FILE = "./digital_twin/Scripts/shared/macro_state.json"
EMA_PERIOD_MACRO = 30 # 设定宏观慢变量的 EMA 周期 (如 30 天)

def calculate_ema(current_val, previous_ema, period=EMA_PERIOD_MACRO):
    """计算指数移动平均 (EMA)"""
    if previous_ema is None:
        return current_val # 初始情况：没有历史 EMA 时，直接返回当前值
    alpha = 2.0 / (period + 1)
    return (alpha * current_val) + ((1 - alpha) * previous_ema)

def load_macro_state():
    """加载历史宏观状态"""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_macro_state(state):
    """保存宏观状态"""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=4)

def calculate_e_macro(net_liquidity_ema, tips_ema):
    """
    计算宏观环境系数 E_macro [-1, 1]
    这里是一个简化的示范模型：
    - net_liquidity_ema: 净流动性 EMA (越大越好)
    - tips_ema: 实际利率 EMA (越小越好)
    """
    # 假设基准值：净流动性中性在 5000B，TIPS 中性在 1.5%
    # 我们可以根据偏离度来计算得分
    
    if net_liquidity_ema is None or tips_ema is None:
        return 0.0 # 初始中性
    
    liq_score = 0
    if net_liquidity_ema > 6000:
        liq_score = 1.0
    elif net_liquidity_ema < 5000:
        liq_score = -1.0
    else:
        liq_score = (net_liquidity_ema - 5000) / 1000.0
        
    tips_score = 0
    if tips_ema > 2.0:
        tips_score = -1.0
    elif tips_ema < 1.0:
        tips_score = 1.0
    else:
        tips_score = (1.5 - tips_ema) / 0.5
        
    # 综合两项指标 (可调整权重)
    e_macro = (liq_score * 0.6) + (tips_score * 0.4)
    
    # 限制在 [-1, 1] 范围内
    return max(min(e_macro, 1.0), -1.0)
