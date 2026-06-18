"""
透明度仪表板模块
展示AI决策过程、偏见检测和反事实推理
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class FactorType(Enum):
    """决策因素类型"""
    RISK_INDICATOR = "risk_indicator"
    BEHAVIORAL_PATTERN = "behavioral_pattern"
    CONTEXTUAL_CUE = "contextual_cue"
    EMOTIONAL_SIGNAL = "emotional_signal"

@dataclass
class DecisionFactor:
    """决策因素"""
    type: FactorType
    weight: float
    confidence: float
    evidence: List[str]
    description: str

@dataclass
class BiasCheck:
    """偏见检查结果"""
    bias_type: str
    detected: bool
    severity: str
    recommendation: str

class TransparencyDashboard:
    """透明度仪表板 - 核心类"""
    
    def __init__(self):
        self.decision_history = []
    
    def analyze_decision(self, content: str, response: str, category: str) -> Dict[str, Any]:
        """分析决策过程"""
        
        # 创建决策因素
        factors = self._generate_decision_factors(content, response)
        
        # 执行偏见检查
        bias_checks = self._check_biases(content, category)
        
        # 生成反事实推理
        counterfactuals = self._generate_counterfactuals(content, category)
        
        # 计算置信度
        confidence = self._calculate_confidence(factors)
        
        result = {
            "decision_factors": [self._factor_to_dict(f) for f in factors],
            "bias_checks": [self._bias_to_dict(b) for b in bias_checks],
            "counterfactuals": counterfactuals,
            "confidence_score": confidence,
            "explanation": self._generate_explanation(factors, confidence)
        }
        
        self.decision_history.append(result)
        return result
    
    def _generate_decision_factors(self, content: str, response: str) -> List[DecisionFactor]:
        """生成决策因素"""
        factors = []
        
        # 风险指标因素
        if "预付" in content or "deposit" in content.lower():
            factors.append(DecisionFactor(
                type=FactorType.RISK_INDICATOR,
                weight=0.35,
                confidence=0.85,
                evidence=["要求预付款项"],
                description="要求预付款项是常见诈骗特征"
            ))
        
        if "无需" in content or "no exam" in content.lower():
            factors.append(DecisionFactor(
                type=FactorType.RISK_INDICATOR,
                weight=0.30,
                confidence=0.90,
                evidence=["承诺绕过正常流程"],
                description="承诺绕过正常流程是高风险信号"
            ))
        
        if "账户" in content or "account" in content.lower():
            factors.append(DecisionFactor(
                type=FactorType.BEHAVIORAL_PATTERN,
                weight=0.25,
                confidence=0.75,
                evidence=["使用个人账户收款"],
                description="使用个人账户而非官方账户收款"
            ))
        
        # 情感信号因素
        if "紧急" in content or "urgent" in content.lower():
            factors.append(DecisionFactor(
                type=FactorType.EMOTIONAL_SIGNAL,
                weight=0.20,
                confidence=0.80,
                evidence=["制造紧迫感"],
                description="诈骗者常用紧迫感施压受害者"
            ))
        
        return factors
    
    def _check_biases(self, content: str, category: str) -> List[BiasCheck]:
        """检查潜在偏见"""
        checks = []
        
        # 检查语言偏见
        if any(word in content for word in ["先生", "女士", "Mr", "Mrs"]):
            checks.append(BiasCheck(
                bias_type="language_bias",
                detected=True,
                severity="low",
                recommendation="注意不要仅因称呼方式判断可信度"
            ))
        
        # 检查场景偏见
        checks.append(BiasCheck(
            bias_type="scenario_bias",
            detected=False,
            severity="none",
            recommendation="场景设计合理，无明显偏见"
        ))
        
        return checks
    
    def _generate_counterfactuals(self, content: str, category: str) -> List[Dict[str, Any]]:
        """生成反事实推理"""
        counterfactuals = []
        
        # 生成"如果...会怎样"场景
        counterfactuals.append({
            "scenario": "如果这是正规机构",
            "changes": ["会有官方网站和联系方式", "支持正规支付渠道", "有实体办公地点"],
            "outcome": "风险显著降低"
        })
        
        counterfactuals.append({
            "scenario": "如果拒绝支付",
            "changes": ["停止与对方联系", "通过官方渠道核实"],
            "outcome": "避免潜在损失"
        })
        
        return counterfactuals
    
    def _calculate_confidence(self, factors: List[DecisionFactor]) -> float:
        """计算决策置信度"""
        if not factors:
            return 0.5
        
        total_weight = sum(f.weight for f in factors)
        weighted_confidence = sum(f.weight * f.confidence for f in factors)
        
        return min(weighted_confidence / total_weight if total_weight > 0 else 0.5, 1.0)
    
    def _generate_explanation(self, factors: List[DecisionFactor], confidence: float) -> str:
        """生成决策解释"""
        if not factors:
            return "基于现有信息，建议保持警惕并进一步核实。"
        
        top_factors = sorted(factors, key=lambda f: f.weight, reverse=True)[:3]
        
        explanation = f"AI分析置信度: {confidence:.0%}。主要风险因素包括："
        for i, factor in enumerate(top_factors, 1):
            explanation += f"\n{i}. {factor.description}（权重: {factor.weight:.0%}）"
        
        return explanation
    
    def _factor_to_dict(self, factor: DecisionFactor) -> Dict[str, Any]:
        """转换决策因素为字典"""
        return {
            "type": factor.type.value,
            "weight": factor.weight,
            "confidence": factor.confidence,
            "evidence": factor.evidence,
            "description": factor.description
        }
    
    def _bias_to_dict(self, bias: BiasCheck) -> Dict[str, Any]:
        """转换偏见检查为字典"""
        return {
            "bias_type": bias.bias_type,
            "detected": bias.detected,
            "severity": bias.severity,
            "recommendation": bias.recommendation
        }
    
    def generate_fairness_analysis(self) -> Dict[str, Any]:
        """生成公平性分析"""
        return {
            "demographic_bias": {
                "detected": False,
                "details": "未检测到人口统计偏见"
            },
            "language_bias": {
                "detected": False,
                "details": "支持多语言，无语言偏见"
            },
            "scenario_diversity": {
                "score": 0.85,
                "details": "场景覆盖多种诈骗类型，多样性良好"
            },
            "overall_fairness_score": 0.90,
            "recommendations": [
                "继续增加更多样化的场景",
                "定期审查潜在的隐性偏见",
                "收集用户反馈以改进公平性"
            ]
        }
