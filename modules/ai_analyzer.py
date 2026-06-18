"""
AI 分析器模块
使用大语言模型分析用户的回答质量
"""

import os
import json
import requests
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class AIAnalysisResult:
    """AI分析结果"""
    score: int
    percentage: int
    level: str
    response_type: str
    identified_risks: List[Dict[str, Any]]
    missed_risks: List[str]
    feedback: str
    reasoning: str

class AIAnalyzer:
    """AI分析器 - 使用大模型评估用户回答"""
    
    def __init__(self, api_key: str = None, model: str = "openai", base_url: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.model = model
        self.base_url = base_url or "https://generativelanguage.googleapis.com/v1beta/openai/"
        
        # 如果使用智谱AI
        if model == "zhipu":
            self.api_key = os.getenv("ZHI_KEY", "")
            self.base_url = "https://open.bigmodel.cn/api/paas/v4"
    
    def analyze_response(self, scenario: Dict, user_response: str) -> AIAnalysisResult:
        """使用AI分析用户回答"""
        
        # 构建提示词
        prompt = self._build_analysis_prompt(scenario, user_response)
        
        try:
            # 调用AI API
            ai_response = self._call_ai_api(prompt)
            
            # 解析AI返回
            result = self._parse_ai_response(ai_response, scenario)
            
            return result
            
        except Exception as e:
            print(f"AI analysis error: {e}")
            # 返回默认结果
            return AIAnalysisResult(
                score=20,
                percentage=0,
                level="poor",
                response_type="unclear",
                identified_risks=[],
                missed_risks=[flag['text'] for flag in scenario.get('red_flags', [])],
                feedback="Unable to analyze response. Please try again.",
                reasoning="AI analysis unavailable"
            )
    
    def _build_analysis_prompt(self, scenario: Dict, user_response: str) -> str:
        """构建分析提示词"""
        
        red_flags_text = "\n".join([
            f"- {flag['text']} (Keywords: {', '.join(flag['keywords'])})"
            for flag in scenario.get('red_flags', [])
        ])
        
        prompt = f"""You are an expert scam identification instructor. Analyze the user's response to determine how well they identified the warning signs.

SCENARIO:
Title: {scenario.get('title', 'Unknown')}
Content: {scenario.get('content', '')}
Sender: {scenario.get('sender', 'Unknown')}

WARNING SIGNS IN THIS SCENARIO:
{red_flags_text}

USER'S RESPONSE:
{user_response}

YOUR TASK:
1. Analyze if the user correctly identified the warning signs
2. Evaluate their understanding of the scam
3. Check if they recognized the appropriate action to take

SCORING CRITERIA:
- 100 points: Identified ALL warning signs with correct reasoning
- 80 points: Identified MOST warning signs (≥70%) with good reasoning
- 60 points: Identified HALF of warning signs (≥50%) with some reasoning
- 40 points: Identified FEW warning signs (≥30%) with minimal reasoning
- 20 points: Failed to identify most warning signs (<30%)

RESPONSE TYPE:
- "reject": User correctly refuses/declines the scam
- "verify": User wants to verify through official channels
- "accept": User incorrectly agrees to the scam
- "unclear": Response is unclear

Respond in JSON format ONLY:
{{
    "score": <integer 20-100>,
    "percentage": <integer 0-100>,
    "level": "<excellent|good|moderate|fair|poor>",
    "response_type": "<reject|verify|accept|unclear>",
    "identified_risks": [
        {{"text": "<risk text>", "keywords": ["matched keyword"]}}
    ],
    "missed_risks": ["<missed risk 1>", "<missed risk 2>"],
    "feedback": "<Detailed feedback in English, 2-3 sentences>",
    "reasoning": "<Brief explanation of the score>"
}}

Analyze the response now:"""
        
        return prompt
    
    def _call_ai_api(self, prompt: str) -> str:
        """调用AI API"""
        
        if self.model == "zhipu":
            return self._call_zhipu_api(prompt)
        else:
            return self._call_openai_compatible_api(prompt)
    
    def _call_openai_compatible_api(self, prompt: str) -> str:
        """调用OpenAI兼容API (Gemini)"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gemini-1.5-flash",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 1000
        }
        
        response = requests.post(
            f"{self.base_url}chat/completions",
            headers=headers,
            json=data,
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            raise Exception(f"API call failed: {response.status_code} - {response.text}")
    
    def _call_zhipu_api(self, prompt: str) -> str:
        """调用智谱AI API"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "glm-4",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 1000
        }
        
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=data,
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            raise Exception(f"API call failed: {response.status_code} - {response.text}")
    
    def _parse_ai_response(self, ai_response: str, scenario: Dict) -> AIAnalysisResult:
        """解析AI返回的JSON"""
        
        try:
            # 提取JSON部分（处理可能的markdown代码块）
            json_text = ai_response
            if "```json" in ai_response:
                json_text = ai_response.split("```json")[1].split("```")[0].strip()
            elif "```" in ai_response:
                json_text = ai_response.split("```")[1].split("```")[0].strip()
            
            # 解析JSON
            result_data = json.loads(json_text)
            
            # 确保所有字段存在
            score = result_data.get('score', 20)
            percentage = result_data.get('percentage', 0)
            level = result_data.get('level', 'poor')
            response_type = result_data.get('response_type', 'unclear')
            identified_risks = result_data.get('identified_risks', [])
            missed_risks = result_data.get('missed_risks', [])
            feedback = result_data.get('feedback', '')
            reasoning = result_data.get('reasoning', '')
            
            return AIAnalysisResult(
                score=score,
                percentage=percentage,
                level=level,
                response_type=response_type,
                identified_risks=identified_risks,
                missed_risks=missed_risks,
                feedback=feedback,
                reasoning=reasoning
            )
            
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}")
            print(f"AI response: {ai_response}")
            
            # 返回默认结果
            return AIAnalysisResult(
                score=20,
                percentage=0,
                level="poor",
                response_type="unclear",
                identified_risks=[],
                missed_risks=[flag['text'] for flag in scenario.get('red_flags', [])],
                feedback="Failed to parse AI response. Please try again.",
                reasoning="Parse error"
            )
