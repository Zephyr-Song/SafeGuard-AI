"""
场景模拟器
负责创建和管理互动式学习场景
"""

import json
import random
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

class ScenarioType(Enum):
    """场景类型"""
    EMAIL = "email"
    MESSAGE = "message"
    JOB_POSTING = "job_posting"
    SOCIAL_MEDIA = "social_media"
    PHONE_CALL = "phone_call"

@dataclass
class SimulationRound:
    """模拟回合"""
    round_number: int
    content: str
    sender_info: Dict[str, str]
    expected_response_type: str
    hints: List[str] = field(default_factory=list)
    red_flags: List[str] = field(default_factory=list)

@dataclass
class SimulationScenario:
    """模拟场景"""
    id: str
    title: str
    category: str
    scenario_type: ScenarioType
    description: str
    rounds: List[SimulationRound]
    learning_objectives: List[str]
    real_world_context: str

class ScenarioSimulator:
    """场景模拟器 - 核心类"""
    
    def __init__(self):
        self.active_simulations = {}
        self.scenario_templates = self._load_templates()
        
    def _load_templates(self) -> Dict[str, Any]:
        """加载场景模板"""
        return {
            "fraudulent_service": {
                "title": "虚假驾校服务",
                "context": "你正在考虑考取驾照，在网上搜索相关信息。",
                "rounds": [
                    {
                        "round": 1,
                        "type": "message",
                        "content": "您好，这里是环城驾校，我们可以代办B1驾照，无需考试，只需支付800元定金和7500元考试费。请转账至账户：6228 4801 2665 3397 775",
                        "sender": {"name": "李教练", "company": "环城驾校"},
                        "hints": ["正规驾校不会承诺'包过'", "要求预付大额费用是危险信号"],
                        "red_flags": ["承诺无需考试", "要求预付费用", "个人账户收款"]
                    },
                    {
                        "round": 2,
                        "type": "message",
                        "content": "您好，定金已收到。现在需要您再支付3000元'加急费'，这样我们可以优先安排您的考试。如果不支付，之前的定金将无法退还。",
                        "sender": {"name": "李教练", "company": "环城驾校"},
                        "hints": ["追加费用是典型诈骗手段", "威胁不退款是施压策略"],
                        "red_flags": ["追加费用", "威胁不退款", "制造紧迫感"]
                    },
                    {
                        "round": 3,
                        "type": "message",
                        "content": "由于系统升级，您需要再支付2000元'系统维护费'。这是最后一次收费，完成后3天内保证出证。",
                        "sender": {"name": "李教练", "company": "环城驾校"},
                        "hints": ["多次收费是诈骗特征", "'最后一次'通常是谎言"],
                        "red_flags": ["多次收费", "虚假承诺", "紧迫感"]
                    }
                ]
            },
            "impersonation": {
                "title": "好友紧急求助",
                "context": "你正在工作中，突然收到微信消息。",
                "rounds": [
                    {
                        "round": 1,
                        "type": "message",
                        "content": "在吗？我是小明，我手机坏了，这是新号。我急用钱，能不能先转5000给我，晚上还你。",
                        "sender": {"name": "小明", "relation": "好友"},
                        "hints": ["新号码需要警惕", "紧急情况往往是诈骗"],
                        "red_flags": ["新号码", "紧急求助", "要求转账"]
                    },
                    {
                        "round": 2,
                        "type": "message",
                        "content": "真的很急，我妈住院了，手术费不够。你先转给我，我明天一定还你。账号：6222 0000 0000 0000",
                        "sender": {"name": "小明", "relation": "好友"},
                        "hints": ["利用同情心", "催促转账是危险信号"],
                        "red_flags": ["利用情感", "催促转账", "无法验证"]
                    }
                ]
            },
            "phishing": {
                "title": "银行安全验证",
                "context": "你收到一条看似来自银行的短信。",
                "rounds": [
                    {
                        "round": 1,
                        "type": "message",
                        "content": "【XX银行】您的账户存在异常登录，请立即点击链接验证身份：http://xxbank-verify.com/safety",
                        "sender": {"name": "XX银行", "type": "官方"},
                        "hints": ["银行不会通过短信发送链接", "应通过官方APP核实"],
                        "red_flags": ["可疑链接", "紧急语气", "要求验证"]
                    },
                    {
                        "round": 2,
                        "type": "email",
                        "content": "尊敬的客户，您的账户将被冻结。请点击以下链接完成身份验证，否则24小时内账户将被锁定。",
                        "sender": {"name": "XX银行安全中心", "email": "security@xxbank-verify.com"},
                        "hints": ["威胁冻结账户是常见手段", "域名与官方不符"],
                        "red_flags": ["威胁冻结", "伪造域名", "制造恐惧"]
                    }
                ]
            },
            "fake_job": {
                "title": "高薪兼职机会",
                "context": "你正在寻找兼职工作，在招聘网站看到一则广告。",
                "rounds": [
                    {
                        "round": 1,
                        "type": "job_posting",
                        "content": "高薪诚聘网络兼职，日薪300-500元，工作时间灵活，无需经验。要求：年满18岁，有手机即可。先交200元培训费，立即上岗。",
                        "sender": {"name": "XX人力资源", "company": "XX科技"},
                        "hints": ["高薪低要求通常是骗局", "要求先付费是危险信号"],
                        "red_flags": ["高薪低要求", "要求先付费", "工作描述模糊"]
                    },
                    {
                        "round": 2,
                        "type": "message",
                        "content": "您好，培训费已收到。现在需要您支付500元'保证金'，工作满一个月退还。这是公司规定，所有员工都需要交。",
                        "sender": {"name": "HR张经理", "company": "XX科技"},
                        "hints": ["多次收费是诈骗特征", "'保证金'通常是借口"],
                        "red_flags": ["多次收费", "虚假承诺", "利用规则"]
                    }
                ]
            },
            "online_relationship": {
                "title": "网络交友陷阱",
                "context": "你在社交软件上认识了一位新朋友。",
                "rounds": [
                    {
                        "round": 1,
                        "type": "message",
                        "content": "你好，看到你的资料觉得我们很有缘分。我在国外工作，平时比较孤单，希望能认识你。",
                        "sender": {"name": "David", "occupation": "工程师", "location": "国外"},
                        "hints": ["国外工作身份需要警惕", "快速建立联系可能是套路"],
                        "red_flags": ["国外身份", "快速建立联系", "表达孤独"]
                    },
                    {
                        "round": 2,
                        "type": "message",
                        "content": "和你聊天真的很开心，感觉找到了知己。我过几个月就回国了，到时候一定要见面。",
                        "sender": {"name": "David", "occupation": "工程师", "location": "国外"},
                        "hints": ["快速升温的感情需警惕", "承诺见面但不具体"],
                        "red_flags": ["快速升温", "模糊承诺", "情感投资"]
                    },
                    {
                        "round": 3,
                        "type": "message",
                        "content": "抱歉，我有个不情之请。我这边遇到点麻烦，需要2万元应急，你能帮我吗？我下周就还你。",
                        "sender": {"name": "David", "occupation": "工程师", "location": "国外"},
                        "hints": ["涉及金钱是危险信号", "网恋诈骗的典型套路"],
                        "red_flags": ["涉及金钱", "编造理由", "利用感情"]
                    }
                ]
            }
        }
    
    def create_simulation(self, category: str, user_id: str) -> SimulationScenario:
        """创建新的模拟场景"""
        template = self.scenario_templates.get(category)
        if not template:
            raise ValueError(f"Unknown category: {category}")
        
        rounds = []
        for r in template["rounds"]:
            rounds.append(SimulationRound(
                round_number=r["round"],
                content=r["content"],
                sender_info=r["sender"],
                expected_response_type=r["type"],
                hints=r.get("hints", []),
                red_flags=r.get("red_flags", [])
            ))
        
        scenario = SimulationScenario(
            id=f"{category}_{random.randint(1000, 9999)}",
            title=template["title"],
            category=category,
            scenario_type=ScenarioType(template["rounds"][0]["type"]),
            description=template["context"],
            rounds=rounds,
            learning_objectives=[
                f"识别{category}类型的诈骗",
                "学会验证信息来源",
                "掌握正确的应对方法"
            ],
            real_world_context=template["context"]
        )
        
        self.active_simulations[user_id] = {
            "scenario": scenario,
            "current_round": 0,
            "responses": [],
            "hints_used": 0
        }
        
        return scenario
    
    def get_current_round(self, user_id: str) -> Optional[SimulationRound]:
        """获取当前回合"""
        sim = self.active_simulations.get(user_id)
        if not sim:
            return None
        
        current = sim["current_round"]
        if current < len(sim["scenario"].rounds):
            return sim["scenario"].rounds[current]
        return None
    
    def process_response(self, user_id: str, response: str) -> Dict[str, Any]:
        """处理用户响应"""
        sim = self.active_simulations.get(user_id)
        if not sim:
            return {"error": "No active simulation"}
        
        current_round = sim["current_round"]
        round_data = sim["scenario"].rounds[current_round]
        
        # 分析响应
        analysis = self._analyze_response(response, round_data)
        
        # 保存响应
        sim["responses"].append({
            "round": current_round + 1,
            "response": response,
            "analysis": analysis
        })
        
        # 推进到下一回合
        sim["current_round"] += 1
        
        # 检查是否完成
        is_complete = sim["current_round"] >= len(sim["scenario"].rounds)
        
        return {
            "analysis": analysis,
            "is_complete": is_complete,
            "next_round": None if is_complete else sim["scenario"].rounds[sim["current_round"]],
            "progress": {
                "current": sim["current_round"],
                "total": len(sim["scenario"].rounds)
            }
        }
    
    def _analyze_response(self, response: str, round_data: SimulationRound) -> Dict[str, Any]:
        """分析用户响应"""
        response_lower = response.lower()
        
        # 检查是否识别了风险
        identified_flags = []
        for flag in round_data.red_flags:
            flag_keywords = flag.lower().split()
            if any(kw in response_lower for kw in flag_keywords):
                identified_flags.append(flag)
        
        # 检查响应类型
        response_type = self._classify_response(response)
        
        # 评估安全性
        safety_score = self._calculate_safety_score(response, identified_flags, round_data)
        
        return {
            "identified_red_flags": identified_flags,
            "missed_red_flags": [f for f in round_data.red_flags if f not in identified_flags],
            "response_type": response_type,
            "safety_score": safety_score,
            "feedback": self._generate_feedback(safety_score, identified_flags, round_data)
        }
    
    def _classify_response(self, response: str) -> str:
        """分类响应类型"""
        response_lower = response.lower()
        
        if any(word in response_lower for word in ["拒绝", "不", "no", "拒绝", "ignore"]):
            return "reject"
        elif any(word in response_lower for word in ["怀疑", "验证", "confirm", "verify", "check"]):
            return "verify"
        elif any(word in response_lower for word in ["相信", "好的", "yes", "ok", "同意"]):
            return "accept"
        else:
            return "unclear"
    
    def _calculate_safety_score(self, response: str, identified_flags: List[str], 
                                round_data: SimulationRound) -> int:
        """计算安全得分"""
        score = 0
        
        # 识别风险点得分
        score += len(identified_flags) * 20
        
        # 响应类型得分
        response_type = self._classify_response(response)
        if response_type == "reject":
            score += 30
        elif response_type == "verify":
            score += 25
        elif response_type == "unclear":
            score += 10
        
        return min(score, 100)
    
    def _generate_feedback(self, score: int, identified_flags: List[str], 
                          round_data: SimulationRound) -> str:
        """生成反馈"""
        if score >= 80:
            return "优秀！你很好地识别了风险并采取了正确的行动。"
        elif score >= 60:
            return "不错！你识别了一些风险，但还有提升空间。"
        elif score >= 40:
            return "需要警惕。建议你重新考虑这个情况的潜在风险。"
        else:
            return "危险！这个情况很可能是诈骗，请立即停止互动。"
    
    def get_hint(self, user_id: str) -> Optional[str]:
        """获取提示"""
        sim = self.active_simulations.get(user_id)
        if not sim:
            return None
        
        current_round = sim["current_round"]
        if current_round < len(sim["scenario"].rounds):
            round_data = sim["scenario"].rounds[current_round]
            if round_data.hints and sim["hints_used"] < len(round_data.hints):
                hint = round_data.hints[sim["hints_used"]]
                sim["hints_used"] += 1
                return hint
        return None
    
    def get_simulation_summary(self, user_id: str) -> Dict[str, Any]:
        """获取模拟总结"""
        sim = self.active_simulations.get(user_id)
        if not sim:
            return {"error": "No active simulation"}
        
        responses = sim["responses"]
        if not responses:
            return {"error": "No responses recorded"}
        
        avg_score = sum(r["analysis"]["safety_score"] for r in responses) / len(responses)
        
        return {
            "scenario_title": sim["scenario"].title,
            "category": sim["scenario"].category,
            "rounds_completed": len(responses),
            "total_rounds": len(sim["scenario"].rounds),
            "average_safety_score": round(avg_score, 2),
            "overall_rating": self._get_overall_rating(avg_score),
            "key_learnings": self._extract_learnings(responses),
            "recommendations": self._generate_recommendations(avg_score, responses)
        }
    
    def _get_overall_rating(self, score: float) -> str:
        """获取总体评级"""
        if score >= 80:
            return "优秀"
        elif score >= 60:
            return "良好"
        elif score >= 40:
            return "需改进"
        else:
            return "需加强学习"
    
    def _extract_learnings(self, responses: List[Dict]) -> List[str]:
        """提取学习要点"""
        learnings = []
        for r in responses:
            missed = r["analysis"].get("missed_red_flags", [])
            for flag in missed:
                learnings.append(f"注意识别：{flag}")
        return list(set(learnings))[:5]  # 最多5条
    
    def _generate_recommendations(self, score: float, responses: List[Dict]) -> List[str]:
        """生成建议"""
        recommendations = []
        
        if score < 60:
            recommendations.append("建议重新学习诈骗识别基础知识")
        
        # 检查是否有接受诈骗的情况
        accept_count = sum(1 for r in responses if r["analysis"]["response_type"] == "accept")
        if accept_count > 0:
            recommendations.append("你在某些情况下过于轻信，需要提高警惕")
        
        if not recommendations:
            recommendations.append("继续保持警惕，可以尝试更复杂的场景")
        
        return recommendations
    
    def end_simulation(self, user_id: str):
        """结束模拟"""
        if user_id in self.active_simulations:
            del self.active_simulations[user_id]
