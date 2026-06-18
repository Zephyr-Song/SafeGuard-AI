"""
学习进度追踪器
追踪用户学习进度、生成报告和提供个性化建议
"""

import json
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum

class AchievementType(Enum):
    """成就类型"""
    FIRST_STEP = "first_step"           # 完成首次学习
    RISK_DETECTOR = "risk_detector"     # 识别所有风险点
    SAFETY_EXPERT = "safety_expert"     # 获得优秀评级
    CATEGORY_MASTER = "category_master" # 完成某类所有场景
    CONSISTENT_LEARNER = "consistent_learner"  # 连续学习
    KNOWLEDGE_SHARER = "knowledge_sharer"      # 分享学习成果

@dataclass
class Achievement:
    """成就"""
    id: str
    name: str
    description: str
    type: AchievementType
    unlocked_at: str
    icon: str

@dataclass
class LearningSession:
    """学习会话"""
    session_id: str
    start_time: str
    end_time: Optional[str]
    category: str
    scenario_id: str
    score: float
    completed: bool
    feedback: Dict[str, Any]

@dataclass
class UserProgress:
    """用户进度"""
    user_id: str
    created_at: str
    last_active: str
    total_sessions: int
    completed_scenarios: List[str]
    category_progress: Dict[str, float]
    achievements: List[Achievement]
    skill_levels: Dict[str, float]
    learning_streak: int
    total_learning_time: int  # minutes

class LearningTracker:
    """学习追踪器 - 核心类"""
    
    def __init__(self, data_dir: str = "data/feedback"):
        self.data_dir = data_dir
        self.user_progress: Dict[str, UserProgress] = {}
        self.current_sessions: Dict[str, LearningSession] = {}
        self.achievements_catalog = self._load_achievements_catalog()
        
        os.makedirs(data_dir, exist_ok=True)
        self._load_all_progress()
    
    def _load_achievements_catalog(self) -> Dict[str, Dict]:
        """加载成就目录"""
        return {
            "first_step": {
                "name": "初次尝试",
                "description": "完成第一次学习场景",
                "icon": "🎯",
                "type": AchievementType.FIRST_STEP
            },
            "risk_detector": {
                "name": "风险侦探",
                "description": "在一次场景中识别所有风险点",
                "icon": "🔍",
                "type": AchievementType.RISK_DETECTOR
            },
            "safety_expert": {
                "name": "安全专家",
                "description": "连续3次获得优秀评级",
                "icon": "🛡️",
                "type": AchievementType.SAFETY_EXPERT
            },
            "category_master": {
                "name": "类别大师",
                "description": "完成某一诈骗类型的所有场景",
                "icon": "📚",
                "type": AchievementType.CATEGORY_MASTER
            },
            "consistent_learner": {
                "name": "坚持学习者",
                "description": "连续7天进行学习",
                "icon": "🔥",
                "type": AchievementType.CONSISTENT_LEARNER
            },
            "knowledge_sharer": {
                "name": "知识传播者",
                "description": "生成并分享学习报告",
                "icon": "📤",
                "type": AchievementType.KNOWLEDGE_SHARER
            }
        }
    
    def _load_all_progress(self):
        """加载所有用户进度"""
        if not os.path.exists(self.data_dir):
            return
        
        for filename in os.listdir(self.data_dir):
            if filename.endswith("_progress.json"):
                user_id = filename.replace("_progress.json", "")
                filepath = os.path.join(self.data_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        self.user_progress[user_id] = self._dict_to_progress(data)
                except Exception as e:
                    print(f"Error loading progress for {user_id}: {e}")
    
    def _dict_to_progress(self, data: Dict) -> UserProgress:
        """字典转进度对象"""
        achievements = [
            Achievement(**a) for a in data.get("achievements", [])
        ]
        return UserProgress(
            user_id=data["user_id"],
            created_at=data["created_at"],
            last_active=data["last_active"],
            total_sessions=data["total_sessions"],
            completed_scenarios=data.get("completed_scenarios", []),
            category_progress=data.get("category_progress", {}),
            achievements=achievements,
            skill_levels=data.get("skill_levels", {}),
            learning_streak=data.get("learning_streak", 0),
            total_learning_time=data.get("total_learning_time", 0)
        )
    
    def _progress_to_dict(self, progress: UserProgress) -> Dict:
        """进度对象转字典"""
        return {
            "user_id": progress.user_id,
            "created_at": progress.created_at,
            "last_active": progress.last_active,
            "total_sessions": progress.total_sessions,
            "completed_scenarios": progress.completed_scenarios,
            "category_progress": progress.category_progress,
            "achievements": [asdict(a) for a in progress.achievements],
            "skill_levels": progress.skill_levels,
            "learning_streak": progress.learning_streak,
            "total_learning_time": progress.total_learning_time
        }
    
    def get_or_create_progress(self, user_id: str) -> UserProgress:
        """获取或创建用户进度"""
        if user_id not in self.user_progress:
            now = datetime.now().isoformat()
            self.user_progress[user_id] = UserProgress(
                user_id=user_id,
                created_at=now,
                last_active=now,
                total_sessions=0,
                completed_scenarios=[],
                category_progress={},
                achievements=[],
                skill_levels={},
                learning_streak=0,
                total_learning_time=0
            )
        return self.user_progress[user_id]
    
    def start_session(self, user_id: str, category: str, scenario_id: str) -> LearningSession:
        """开始新会话"""
        session_id = f"{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        session = LearningSession(
            session_id=session_id,
            start_time=datetime.now().isoformat(),
            end_time=None,
            category=category,
            scenario_id=scenario_id,
            score=0.0,
            completed=False,
            feedback={}
        )
        self.current_sessions[user_id] = session
        return session
    
    def end_session(self, user_id: str, score: float, feedback: Dict[str, Any]):
        """结束会话"""
        session = self.current_sessions.get(user_id)
        if not session:
            return
        
        session.end_time = datetime.now().isoformat()
        session.score = score
        session.completed = True
        session.feedback = feedback
        
        # 更新用户进度
        progress = self.get_or_create_progress(user_id)
        progress.total_sessions += 1
        progress.last_active = datetime.now().isoformat()
        progress.completed_scenarios.append(session.scenario_id)
        
        # 更新类别进度
        category = session.category
        if category not in progress.category_progress:
            progress.category_progress[category] = 0.0
        progress.category_progress[category] = min(
            100.0, progress.category_progress[category] + 10.0
        )
        
        # 更新技能水平
        if category not in progress.skill_levels:
            progress.skill_levels[category] = 0.0
        progress.skill_levels[category] = (
            progress.skill_levels[category] * 0.7 + score * 0.3
        )
        
        # 计算学习时间
        start = datetime.fromisoformat(session.start_time)
        end = datetime.fromisoformat(session.end_time)
        duration = int((end - start).total_seconds() / 60)
        progress.total_learning_time += duration
        
        # 检查成就
        self._check_achievements(user_id, progress, session)
        
        # 保存进度
        self._save_progress(user_id)
        
        # 清理当前会话
        del self.current_sessions[user_id]
    
    def _check_achievements(self, user_id: str, progress: UserProgress, 
                           session: LearningSession):
        """检查并授予成就"""
        unlocked = []
        
        # 首次学习成就
        if progress.total_sessions == 1:
            unlocked.append("first_step")
        
        # 风险侦探成就
        if session.score >= 100:
            unlocked.append("risk_detector")
        
        # 安全专家成就
        recent_sessions = self._get_recent_sessions(user_id, 3)
        if all(s.score >= 80 for s in recent_sessions):
            unlocked.append("safety_expert")
        
        # 类别大师成就
        if progress.category_progress.get(session.category, 0) >= 100:
            unlocked.append("category_master")
        
        # 授予新成就
        existing_ids = {a.id for a in progress.achievements}
        for achievement_id in unlocked:
            if achievement_id not in existing_ids:
                catalog_item = self.achievements_catalog.get(achievement_id)
                if catalog_item:
                    achievement = Achievement(
                        id=achievement_id,
                        name=catalog_item["name"],
                        description=catalog_item["description"],
                        type=catalog_item["type"],
                        unlocked_at=datetime.now().isoformat(),
                        icon=catalog_item["icon"]
                    )
                    progress.achievements.append(achievement)
    
    def _get_recent_sessions(self, user_id: str, count: int) -> List[LearningSession]:
        """获取最近会话"""
        # 这里简化处理，实际应该从存储中读取
        return []
    
    def _save_progress(self, user_id: str):
        """保存用户进度"""
        progress = self.user_progress.get(user_id)
        if not progress:
            return
        
        filepath = os.path.join(self.data_dir, f"{user_id}_progress.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self._progress_to_dict(progress), f, ensure_ascii=False, indent=2)
    
    def get_progress_summary(self, user_id: str) -> Dict[str, Any]:
        """获取进度摘要"""
        progress = self.get_or_create_progress(user_id)
        
        return {
            "user_id": user_id,
            "member_since": progress.created_at,
            "total_sessions": progress.total_sessions,
            "total_learning_time": progress.total_learning_time,
            "learning_streak": progress.learning_streak,
            "achievements_count": len(progress.achievements),
            "achievements": [
                {"name": a.name, "icon": a.icon, "description": a.description}
                for a in progress.achievements
            ],
            "category_progress": progress.category_progress,
            "skill_levels": {
                k: round(v, 1) for k, v in progress.skill_levels.items()
            },
            "overall_progress": self._calculate_overall_progress(progress)
        }
    
    def _calculate_overall_progress(self, progress: UserProgress) -> float:
        """计算整体进度"""
        if not progress.category_progress:
            return 0.0
        
        total = sum(progress.category_progress.values())
        count = len(progress.category_progress)
        return round(total / count, 1) if count > 0 else 0.0
    
    def generate_learning_report(self, user_id: str) -> Dict[str, Any]:
        """生成学习报告"""
        progress = self.get_or_create_progress(user_id)
        
        # 计算统计数据
        category_stats = {}
        for cat, score in progress.skill_levels.items():
            category_stats[cat] = {
                "skill_level": round(score, 1),
                "progress": progress.category_progress.get(cat, 0),
                "status": self._get_category_status(score)
            }
        
        # 生成建议
        recommendations = self._generate_recommendations(progress)
        
        return {
            "report_date": datetime.now().isoformat(),
            "user_summary": {
                "total_sessions": progress.total_sessions,
                "total_learning_time_hours": round(progress.total_learning_time / 60, 1),
                "achievements_earned": len(progress.achievements),
                "current_streak": progress.learning_streak
            },
            "category_performance": category_stats,
            "strengths": self._identify_strengths(progress),
            "areas_for_improvement": self._identify_weaknesses(progress),
            "recommendations": recommendations,
            "next_milestones": self._get_next_milestones(progress)
        }
    
    def _get_category_status(self, score: float) -> str:
        """获取类别状态"""
        if score >= 80:
            return "优秀"
        elif score >= 60:
            return "良好"
        elif score >= 40:
            return "需改进"
        else:
            return "初学"
    
    def _identify_strengths(self, progress: UserProgress) -> List[str]:
        """识别优势领域"""
        strengths = []
        for cat, score in progress.skill_levels.items():
            if score >= 70:
                strengths.append(f"{cat}: 表现出色")
        return strengths if strengths else ["继续学习以发现您的优势领域"]
    
    def _identify_weaknesses(self, progress: UserProgress) -> List[str]:
        """识别需要改进的领域"""
        weaknesses = []
        for cat, score in progress.skill_levels.items():
            if score < 50:
                weaknesses.append(f"{cat}: 需要加强练习")
        return weaknesses if weaknesses else ["整体表现良好，继续保持"]
    
    def _generate_recommendations(self, progress: UserProgress) -> List[str]:
        """生成学习建议"""
        recommendations = []
        
        # 基于进度生成建议
        if progress.total_sessions < 5:
            recommendations.append("建议多尝试不同类型的诈骗场景")
        
        # 基于类别进度生成建议
        low_progress_cats = [
            cat for cat, prog in progress.category_progress.items() 
            if prog < 50
        ]
        if low_progress_cats:
            recommendations.append(f"建议重点学习: {', '.join(low_progress_cats)}")
        
        # 基于技能水平生成建议
        low_skill_cats = [
            cat for cat, skill in progress.skill_levels.items() 
            if skill < 50
        ]
        if low_skill_cats:
            recommendations.append(f"以下类别需要加强练习: {', '.join(low_skill_cats)}")
        
        if not recommendations:
            recommendations.append("您已经掌握了很好的防诈骗知识，可以尝试教授他人！")
        
        return recommendations
    
    def _get_next_milestones(self, progress: UserProgress) -> List[Dict[str, Any]]:
        """获取下一个里程碑"""
        milestones = []
        
        # 会话里程碑
        next_session_milestone = ((progress.total_sessions // 10) + 1) * 10
        milestones.append({
            "type": "sessions",
            "target": next_session_milestone,
            "current": progress.total_sessions,
            "description": f"完成{next_session_milestone}次学习会话"
        })
        
        # 成就里程碑
        next_achievement_count = ((len(progress.achievements) // 3) + 1) * 3
        milestones.append({
            "type": "achievements",
            "target": next_achievement_count,
            "current": len(progress.achievements),
            "description": f"获得{next_achievement_count}个成就"
        })
        
        return milestones
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取排行榜"""
        users = []
        for user_id, progress in self.user_progress.items():
            users.append({
                "user_id": user_id,
                "total_sessions": progress.total_sessions,
                "achievements": len(progress.achievements),
                "overall_progress": self._calculate_overall_progress(progress),
                "skill_average": sum(progress.skill_levels.values()) / len(progress.skill_levels) 
                                if progress.skill_levels else 0
            })
        
        # 按成就数和进度排序
        users.sort(key=lambda x: (x["achievements"], x["overall_progress"]), reverse=True)
        return users[:limit]
