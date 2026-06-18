"""
测试AI分析器
"""

import sys
import os

# 添加模块路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.ai_analyzer import AIAnalyzer

# 测试场景
test_scenario = {
    "title": "Fake Driving School",
    "content": "Hello, this is City Driving School. We can help you get a B1 driver's license without taking the exam. Just pay a deposit of 800 yuan and an exam fee of 7,500 yuan. Transfer to account: 6228 4801 2665 3397 775",
    "sender": "Coach Li",
    "red_flags": [
        {
            "text": "Promises no exam required",
            "keywords": ["no exam", "without exam", "no test", "skip exam"]
        },
        {
            "text": "Requests upfront payment",
            "keywords": ["deposit", "prepay", "upfront", "pay first"]
        },
        {
            "text": "Personal bank account",
            "keywords": ["account", "transfer", "bank"]
        }
    ]
}

# 测试用户回答
test_responses = [
    "This is clearly a scam! They promise no exam which is impossible, and they want me to pay upfront to a personal account. I should verify with official driving schools.",
    "I think I should pay the deposit to get my license quickly.",
    "I'm not sure if this is legitimate. Let me check the driving school's official website first."
]

def test_ai_analyzer():
    """测试AI分析器"""
    
    print("=" * 60)
    print("Testing AI Analyzer")
    print("=" * 60)
    
    # 初始化分析器
    analyzer = AIAnalyzer()
    
    for i, response in enumerate(test_responses, 1):
        print(f"\n[Test {i}]")
        print(f"User Response: {response}")
        print("-" * 60)
        
        # 分析回答
        result = analyzer.analyze_response(test_scenario, response)
        
        # 显示结果
        print(f"Score: {result.score}/100")
        print(f"Level: {result.level}")
        print(f"Response Type: {result.response_type}")
        print(f"Identified Risks: {result.identified_risks}")
        print(f"Missed Risks: {result.missed_risks}")
        print(f"Feedback: {result.feedback}")
        print("=" * 60)

if __name__ == "__main__":
    test_ai_analyzer()
