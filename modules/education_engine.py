"""
教育内容生成引擎
负责生成个性化的安全教育内容和学习路径
"""

import json
import random
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class LearningStage(Enum):
    """学习阶段"""
    AWARENESS = "awareness"        # 意识建立
    KNOWLEDGE = "knowledge"        # 知识学习
    PRACTICE = "practice"          # 实践练习
    REFLECTION = "reflection"      # 反思总结

@dataclass
class LearningObjective:
    """学习目标"""
    id: str
    description: str
    category: str
    difficulty: str
    expected_outcome: str

@dataclass
class EducationalScenario:
    """教育场景"""
    id: str
    category: str
    stage: LearningStage
    content: str
    red_flags: List[str]
    learning_points: List[str]
    reflection_questions: List[str]

class EducationEngine:
    """教育引擎 - 核心类"""
    
    def __init__(self, difficulty: str = "beginner"):
        self.difficulty = difficulty
        self.learning_history = []
        self.current_stage = LearningStage.AWARENESS
        self.scenarios = self._load_scenarios()
        
    def _load_scenarios(self) -> Dict[str, List[EducationalScenario]]:
        """加载教育场景"""
        # 基于Fraud-R1数据集构建的教育场景
        scenarios = {
            "fraudulent_service": [
                EducationalScenario(
                    id="fs_001",
                    category="fraudulent_service",
                    stage=LearningStage.AWARENESS,
                    content="你收到一条短信：'您好，这里是环城驾校，我们可以代办B1驾照，只需先支付800元定金和考试费。'",
                    red_flags=[
                        "要求预付费用",
                        "承诺可以快速获得驾照",
                        "非官方渠道联系"
                    ],
                    learning_points=[
                        "正规驾校不会承诺'包过'",
                        "驾照考试必须通过正规渠道",
                        "预付费用是常见诈骗手段"
                    ],
                    reflection_questions=[
                        "为什么正规机构不会要求预付大额费用？",
                        "如何验证驾校的真实性？"
                    ]
                ),
                EducationalScenario(
                    id="fs_002",
                    category="fraudulent_service",
                    stage=LearningStage.PRACTICE,
                    content="你收到一封邮件，声称来自某知名电商平台客服，说你的账户有异常交易，需要你提供账户余额进行验证。",
                    red_flags=[
                        "要求提供敏感信息",
                        "制造紧急感",
                        "非官方邮箱地址"
                    ],
                    learning_points=[
                        "正规平台不会通过邮件索要账户信息",
                        "应通过官方APP或网站核实",
                        "异常交易应直接联系官方客服"
                    ],
                    reflection_questions=[
                        "收到可疑邮件时，正确的处理步骤是什么？",
                        "如何识别伪造的官方邮件？"
                    ]
                )
            ],
            "impersonation": [
                EducationalScenario(
                    id="imp_001",
                    category="impersonation",
                    stage=LearningStage.AWARENESS,
                    content="你收到微信消息，头像和昵称都显示是你的好友'小明'，他说急需用钱，让你转账5000元。",
                    red_flags=[
                        "紧急求助",
                        "要求转账",
                        "无法语音或视频确认"
                    ],
                    learning_points=[
                        "应通过其他渠道确认身份",
                        "紧急情况更可能是诈骗",
                        "转账前务必多方核实"
                    ],
                    reflection_questions=[
                        "如何确认对方真实身份？",
                        "为什么诈骗者喜欢制造紧急感？"
                    ]
                )
            ],
            "phishing": [
                EducationalScenario(
                    id="phi_001",
                    category="phishing",
                    stage=LearningStage.KNOWLEDGE,
                    content="你收到一条短信：'您的快递已到达，点击链接查看详情：http://t.cn/xxxxx'",
                    red_flags=[
                        "短链接",
                        "要求点击链接",
                        "未提及具体快递公司"
                    ],
                    learning_points=[
                        "不要点击不明链接",
                        "应通过官方APP查询快递",
                        "短链接可能隐藏恶意网站"
                    ],
                    reflection_questions=[
                        "如何安全地查询快递信息？",
                        "点击不明链接可能有什么风险？"
                    ]
                )
            ],
            "fake_job": [
                EducationalScenario(
                    id="fj_001",
                    category="fake_job",
                    stage=LearningStage.PRACTICE,
                    content="你在招聘网站看到一则广告：'高薪诚聘，日薪500元，无需经验，在家即可工作，先交300元培训费。'",
                    red_flags=[
                        "高薪低要求",
                        "要求先付费",
                        "工作内容模糊"
                    ],
                    learning_points=[
                        "正规招聘不会要求先付费",
                        "高薪往往对应高要求",
                        "应核实公司真实性"
                    ],
                    reflection_questions=[
                        "为什么正规公司不会要求求职者先付费？",
                        "如何核实招聘信息的真实性？"
                    ]
                )
            ],
            "online_relationship": [
                EducationalScenario(
                    id="or_001",
                    category="online_relationship",
                    stage=LearningStage.REFLECTION,
                    content="你在社交软件上认识了一位网友，聊得很投机。一周后，对方说家人生病急需用钱，向你借2万元。",
                    red_flags=[
                        "快速建立感情",
                        "各种理由要钱",
                        "拒绝见面或视频"
                    ],
                    learning_points=[
                        "网络交友需谨慎",
                        "涉及金钱应提高警惕",
                        "真实感情不会急于谈钱"
                    ],
                    reflection_questions=[
                        "为什么网恋诈骗容易得手？",
                        "如何在网络交友中保护自己？"
                    ]
                )
            ]
        }
        return scenarios
    
    def get_next_scenario(self, category: Optional[str] = None) -> EducationalScenario:
        """获取下一个学习场景"""
        if category and category in self.scenarios:
            available = self.scenarios[category]
        else:
            # 随机选择一个类别
            available = random.choice(list(self.scenarios.values()))
        
        # 根据当前阶段筛选
        stage_scenarios = [s for s in available if s.stage == self.current_stage]
        if not stage_scenarios:
            stage_scenarios = available
            
        return random.choice(stage_scenarios)
    
    def advance_stage(self):
        """推进到下一个学习阶段"""
        stages = list(LearningStage)
        current_idx = stages.index(self.current_stage)
        if current_idx < len(stages) - 1:
            self.current_stage = stages[current_idx + 1]
            return True
        return False
    
    def generate_learning_path(self, user_profile: Dict[str, Any]) -> List[LearningObjective]:
        """生成个性化学习路径"""
        objectives = []
        
        # 根据用户档案确定学习重点
        if user_profile.get("experience_level") == "beginner":
            objectives.extend([
                LearningObjective(
                    id="obj_001",
                    description="识别常见的诈骗类型",
                    category="awareness",
                    difficulty="beginner",
                    expected_outcome="能够识别5种常见诈骗"
                ),
                LearningObjective(
                    id="obj_002",
                    description="学会验证信息来源",
                    category="skill",
                    difficulty="beginner",
                    expected_outcome="能够独立验证可疑信息"
                )
            ])
        
        return objectives
    
    def provide_feedback(self, user_response: str, scenario: EducationalScenario) -> Dict[str, Any]:
        """提供学习反馈"""
        # 分析用户响应
        identified_flags = []
        missed_flags = []
        
        for flag in scenario.red_flags:
            if any(keyword in user_response.lower() for keyword in flag.lower().split()):
                identified_flags.append(flag)
            else:
                missed_flags.append(flag)
        
        # 计算得分
        score = len(identified_flags) / len(scenario.red_flags) if scenario.red_flags else 0
        
        return {
            "score": round(score * 100, 2),
            "identified_flags": identified_flags,
            "missed_flags": missed_flags,
            "learning_points": scenario.learning_points,
            "next_steps": self._suggest_next_steps(score)
        }
    
    def _suggest_next_steps(self, score: float) -> List[str]:
        """建议下一步学习"""
        if score < 0.4:
            return [
                "建议重新学习基础知识",
                "尝试更简单的场景",
                "查看学习提示"
            ]
        elif score < 0.7:
            return [
                "继续练习类似场景",
                "重点关注遗漏的风险点",
                "阅读相关案例"
            ]
        else:
            return [
                "尝试更复杂的场景",
                "学习其他诈骗类型",
                "分享给朋友家人"
            ]
    
    def generate_report(self) -> Dict[str, Any]:
        """生成学习报告"""
        return {
            "learning_stage": self.current_stage.value,
            "scenarios_completed": len(self.learning_history),
            "categories_covered": list(set(h.get("category") for h in self.learning_history)),
            "average_score": self._calculate_average_score(),
            "recommendations": self._generate_recommendations()
        }
    
    def _calculate_average_score(self) -> float:
        """计算平均得分"""
        if not self.learning_history:
            return 0.0
        scores = [h.get("score", 0) for h in self.learning_history]
        return round(sum(scores) / len(scores), 2)
    
    def _generate_recommendations(self) -> List[str]:
        """生成学习建议"""
        recommendations = []
        avg_score = self._calculate_average_score()
        
        if avg_score < 50:
            recommendations.append("建议从基础知识开始学习")
        elif avg_score < 75:
            recommendations.append("继续加强练习，重点关注风险识别")
        else:
            recommendations.append("表现优秀！可以尝试教授他人")
            
        return recommendations
