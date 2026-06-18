"""
安全守护模块
负责内容 distress 检测、创伤知情安全检查和情绪状态监控
"""

import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class DistressLevel(Enum):
    """困扰程度"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SafetyAction(Enum):
    """安全行动"""
    CONTINUE = "continue"
    PROVIDE_RESOURCES = "provide_resources"
    PAUSE_AND_CHECK = "pause_and_check"
    ESCALATE = "escalate"
    STOP = "stop"

@dataclass
class EmotionalState:
    """情绪状态"""
    anxiety_level: float  # 0-1
    confusion_level: float  # 0-1
    distress_level: float  # 0-1
    engagement_level: float  # 0-1
    overall_wellbeing: str  # good, moderate, concerning

@dataclass
class SafetyCheck:
    """安全检查"""
    is_safe: bool
    distress_detected: bool
    distress_level: DistressLevel
    action_required: SafetyAction
    message: str
    resources: List[str]

class SafetyGuardian:
    """安全守护模块 - 核心类"""
    
    def __init__(self):
        self.distress_keywords = {
            DistressLevel.LOW: [
                "有点担心", "不太确定", "困惑", "confused", "unsure", "worried"
            ],
            DistressLevel.MEDIUM: [
                "害怕", "焦虑", "紧张", "scared", "anxious", "nervous", 
                "害怕", "担心", "不安"
            ],
            DistressLevel.HIGH: [
                "恐慌", "恐惧", "崩溃", "panic", "terrified", "overwhelmed",
                "受不了", "绝望"
            ],
            DistressLevel.CRITICAL: [
                "自杀", "自残", "不想活了", "suicide", "self-harm", "kill myself",
                "结束生命", "想死"
            ]
        }
        
        self.trauma_keywords = [
            "创伤", "虐待", "暴力", "trauma", "abuse", "violence",
            "受害", "victim", "伤害", "hurt"
        ]
        
        self.emotional_history = []
        
    def check_content_safety(self, content: str, context: str = "") -> SafetyCheck:
        """检查内容安全性"""
        
        # 检测困扰程度
        distress_level = self._detect_distress(content)
        
        # 检测创伤相关内容
        trauma_detected = self._detect_trauma_content(content)
        
        # 评估情绪状态
        emotional_state = self._assess_emotional_state(content)
        self.emotional_history.append(emotional_state)
        
        # 确定行动
        action, message, resources = self._determine_action(
            distress_level, trauma_detected, emotional_state, context
        )
        
        return SafetyCheck(
            is_safe=distress_level != DistressLevel.CRITICAL,
            distress_detected=distress_level != DistressLevel.NONE,
            distress_level=distress_level,
            action_required=action,
            message=message,
            resources=resources
        )
    
    def _detect_distress(self, content: str) -> DistressLevel:
        """检测困扰程度"""
        content_lower = content.lower()
        
        # 检查各级别关键词
        for level in [DistressLevel.CRITICAL, DistressLevel.HIGH, 
                      DistressLevel.MEDIUM, DistressLevel.LOW]:
            keywords = self.distress_keywords.get(level, [])
            if any(kw in content_lower for kw in keywords):
                return level
        
        return DistressLevel.NONE
    
    def _detect_trauma_content(self, content: str) -> bool:
        """检测创伤相关内容"""
        content_lower = content.lower()
        return any(kw in content_lower for kw in self.trauma_keywords)
    
    def _assess_emotional_state(self, content: str) -> EmotionalState:
        """评估情绪状态"""
        content_lower = content.lower()
        
        # 焦虑指标
        anxiety_keywords = ["焦虑", "担心", "害怕", "紧张", "anxious", "worried", "nervous"]
        anxiety_count = sum(1 for kw in anxiety_keywords if kw in content_lower)
        anxiety_level = min(anxiety_count * 0.2, 1.0)
        
        # 困惑指标
        confusion_keywords = ["困惑", "不明白", "不懂", "confused", "unclear", "don't understand"]
        confusion_count = sum(1 for kw in confusion_keywords if kw in content_lower)
        confusion_level = min(confusion_count * 0.25, 1.0)
        
        # 困扰指标
        distress_level = self._detect_distress(content)
        distress_value = {
            DistressLevel.NONE: 0.0,
            DistressLevel.LOW: 0.25,
            DistressLevel.MEDIUM: 0.5,
            DistressLevel.HIGH: 0.75,
            DistressLevel.CRITICAL: 1.0
        }.get(distress_level, 0.0)
        
        # 参与度指标（基于内容长度和细节）
        engagement_level = min(len(content) / 200, 1.0)
        
        # 整体健康状态
        wellbeing_score = 1 - (anxiety_level + confusion_level + distress_value) / 3
        if wellbeing_score > 0.7:
            overall_wellbeing = "good"
        elif wellbeing_score > 0.4:
            overall_wellbeing = "moderate"
        else:
            overall_wellbeing = "concerning"
        
        return EmotionalState(
            anxiety_level=round(anxiety_level, 2),
            confusion_level=round(confusion_level, 2),
            distress_level=round(distress_value, 2),
            engagement_level=round(engagement_level, 2),
            overall_wellbeing=overall_wellbeing
        )
    
    def _determine_action(self, distress_level: DistressLevel, 
                         trauma_detected: bool,
                         emotional_state: EmotionalState,
                         context: str) -> tuple:
        """确定行动方案"""
        
        # 紧急情况
        if distress_level == DistressLevel.CRITICAL:
            return (
                SafetyAction.ESCALATE,
                "我们注意到您可能正在经历困难。您的安全和健康是最重要的。",
                [
                    "全国24小时心理援助热线：400-161-9995",
                    "北京心理危机研究与干预中心：010-82951332",
                    "紧急情况请拨打：110（报警）/ 120（急救）"
                ]
            )
        
        # 高度困扰
        if distress_level == DistressLevel.HIGH or emotional_state.overall_wellbeing == "concerning":
            return (
                SafetyAction.PAUSE_AND_CHECK,
                "我们注意到这个内容可能让您感到不安。让我们暂停一下，确保您感觉良好再继续。",
                [
                    "如果感到不适，请随时休息",
                    "可以与家人或朋友讨论您的感受",
                    "全国心理援助热线：400-161-9995"
                ]
            )
        
        # 中度困扰或创伤内容
        if distress_level == DistressLevel.MEDIUM or trauma_detected:
            return (
                SafetyAction.PROVIDE_RESOURCES,
                "这个学习内容可能有些挑战性。如果您感到不适，请记住可以随时暂停。",
                [
                    "学习防诈骗知识是为了保护自己",
                    "感到担心是正常的反应",
                    "如有需要，可以寻求专业心理咨询"
                ]
            )
        
        # 轻度困扰
        if distress_level == DistressLevel.LOW:
            return (
                SafetyAction.CONTINUE,
                "感谢您参与学习。记住，识别诈骗是为了更好地保护自己。",
                [
                    "保持警惕是保护自己的第一步",
                    "有任何疑问都可以寻求帮助"
                ]
            )
        
        # 无困扰
        return (
            SafetyAction.CONTINUE,
            "学习进展顺利！继续保持。",
            []
        )
    
    def get_learning_recommendations(self) -> List[str]:
        """获取学习建议"""
        if not self.emotional_history:
            return ["开始您的学习之旅！"]
        
        recent_states = self.emotional_history[-5:]
        avg_anxiety = sum(s.anxiety_level for s in recent_states) / len(recent_states)
        avg_distress = sum(s.distress_level for s in recent_states) / len(recent_states)
        
        recommendations = []
        
        if avg_anxiety > 0.5:
            recommendations.append("您似乎有些焦虑。建议放慢学习节奏，适时休息。")
        
        if avg_distress > 0.5:
            recommendations.append("学习内容可能让您感到压力。建议从更简单的场景开始。")
        
        if not recommendations:
            recommendations.append("您的学习状态良好！可以尝试更具挑战性的场景。")
        
        recommendations.append("记住：学习防诈骗知识是为了增强自信，不是增加焦虑。")
        
        return recommendations
    
    def generate_safety_report(self) -> Dict[str, Any]:
        """生成安全报告"""
        if not self.emotional_history:
            return {"message": "暂无情绪数据"}
        
        recent_states = self.emotional_history[-10:]
        
        return {
            "total_interactions": len(self.emotional_history),
            "recent_wellbeing": recent_states[-1].overall_wellbeing if recent_states else "unknown",
            "average_anxiety": round(sum(s.anxiety_level for s in recent_states) / len(recent_states), 2),
            "average_distress": round(sum(s.distress_level for s in recent_states) / len(recent_states), 2),
            "average_engagement": round(sum(s.engagement_level for s in recent_states) / len(recent_states), 2),
            "safety_status": self._assess_overall_safety(recent_states),
            "recommendations": self.get_learning_recommendations()
        }
    
    def _assess_overall_safety(self, states: List[EmotionalState]) -> str:
        """评估整体安全状态"""
        if not states:
            return "unknown"
        
        concerning_count = sum(1 for s in states if s.overall_wellbeing == "concerning")
        
        if concerning_count >= len(states) * 0.5:
            return "需要关注"
        elif concerning_count > 0:
            return "基本安全"
        else:
            return "状态良好"
    
    def pre_content_warning(self, scenario_category: str) -> Dict[str, Any]:
        """内容前置警告"""
        warnings = {
            "fraudulent_service": {
                "warning": "以下内容涉及虚假服务诈骗场景",
                "description": "您将学习如何识别伪装成正规服务的诈骗行为。",
                "preparation_tips": [
                    "记住：正规机构不会要求预付大额费用",
                    "保持冷静，不要被优惠承诺迷惑"
                ]
            },
            "impersonation": {
                "warning": "以下内容涉及身份冒充诈骗场景",
                "description": "您将学习如何识别冒充熟人或官方机构的诈骗。",
                "preparation_tips": [
                    "记住：紧急情况往往是诈骗的常用手段",
                    "转账前务必通过其他渠道确认身份"
                ]
            },
            "phishing": {
                "warning": "以下内容涉及钓鱼诈骗场景",
                "description": "您将学习如何识别虚假链接和网站。",
                "preparation_tips": [
                    "不要点击不明链接",
                    "通过官方APP或网站核实信息"
                ]
            },
            "fake_job": {
                "warning": "以下内容涉及虚假招聘场景",
                "description": "您将学习如何识别以招聘为名的诈骗。",
                "preparation_tips": [
                    "正规招聘不会要求先付费",
                    "高薪往往对应高要求"
                ]
            },
            "online_relationship": {
                "warning": "以下内容涉及网恋诈骗场景",
                "description": "您将学习如何识别通过感情关系进行的诈骗。",
                "preparation_tips": [
                    "网络交友需谨慎",
                    "真实感情不会急于谈钱"
                ]
            }
        }
        
        return warnings.get(scenario_category, {
            "warning": "学习内容即将开始",
            "description": "您将进入互动学习场景。",
            "preparation_tips": ["保持开放的心态", "随时可以暂停休息"]
        })
    
    def check_interaction_health(self) -> Dict[str, Any]:
        """检查互动健康度"""
        if len(self.emotional_history) < 3:
            return {"status": "insufficient_data", "message": "需要更多互动数据"}
        
        recent = self.emotional_history[-3:]
        
        # 检查情绪趋势
        anxiety_trend = recent[-1].anxiety_level - recent[0].anxiety_level
        distress_trend = recent[-1].distress_level - recent[0].distress_level
        
        status = "healthy"
        message = "互动状态良好"
        
        if anxiety_trend > 0.3 or distress_trend > 0.3:
            status = "declining"
            message = "检测到情绪压力上升，建议休息"
        elif anxiety_trend < -0.2 and distress_trend < -0.2:
            status = "improving"
            message = "情绪状态正在改善"
        
        return {
            "status": status,
            "message": message,
            "anxiety_trend": round(anxiety_trend, 2),
            "distress_trend": round(distress_trend, 2),
            "suggestion": "建议适当休息" if status == "declining" else "继续保持"
        }
