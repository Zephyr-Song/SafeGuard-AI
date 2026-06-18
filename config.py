# 核心配置文件
import os

# ========== API 配置 ==========
# 智谱 AI (GLM-4)
ZHI_KEY = os.getenv("ZHI_KEY", "")
ZHI_MODEL = "glm-4"
ZHI_URL = "https://open.bigmodel.cn/api/paas/v4"

# OpenAI 兼容 API (Google Gemini)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
OPENAI_MODEL = "gemini-1.5-flash"

# 默认使用的模型
ACTIVE_MODEL = os.getenv("ACTIVE_MODEL", "openai")

# ========== 模拟模式 ==========
# 设置为True时，使用模拟数据而不是真实API调用
MOCK_MODE = os.getenv("MOCK_MODE", "False").lower() == "true"

# ========== API 设置 ==========
API_TIMEOUT = 60
API_MAX_RETRIES = 3
API_RETRY_BACKOFF = 1.8

# ========== 采样参数 ==========
JUDGE_TEMPERATURE = 0.0
JUDGE_TOP_P = 1.0
EDUCATION_TEMPERATURE = 0.7
EDUCATION_TOP_P = 0.95

# ========== 安全教育配置 ==========
# 学习难度级别
DIFFICULTY_LEVELS = {
    "beginner": {"name": "初学者", "rounds": 2, "hints": True},
    "intermediate": {"name": "进阶", "rounds": 3, "hints": True},
    "advanced": {"name": "专家", "rounds": 4, "hints": False}
}

# 诈骗类型配置
FRAUD_CATEGORIES = {
    "fraudulent_service": {
        "name": "虚假服务",
        "name_en": "Fraudulent Service",
        "description": "伪装成正规服务机构的诈骗",
        "warning_signs": ["要求预付费用", "非官方联系方式", "过于优惠的价格"]
    },
    "impersonation": {
        "name": "身份冒充",
        "name_en": "Impersonation",
        "description": "冒充熟人、官方机构或权威人士",
        "warning_signs": ["紧急求助", "要求保密", "账户异常通知"]
    },
    "phishing": {
        "name": "钓鱼诈骗",
        "name_en": "Phishing Scam",
        "description": "通过虚假链接或网站窃取信息",
        "warning_signs": ["可疑链接", "要求输入密码", "拼写错误"]
    },
    "fake_job": {
        "name": "虚假招聘",
        "name_en": "Fake Job Posting",
        "description": "以招聘为名的诈骗",
        "warning_signs": ["高薪低要求", "要求支付费用", "面试流程异常"]
    },
    "online_relationship": {
        "name": "网恋诈骗",
        "name_en": "Online Relationship",
        "description": "通过感情关系进行的诈骗",
        "warning_signs": ["快速建立感情", "拒绝见面", "各种理由要钱"]
    }
}

# ========== 安全守护配置 ==========
SAFETY_CONFIG = {
    "distress_keywords": ["害怕", "焦虑", "恐慌", " distress", "upset", "worried"],
    "max_interaction_rounds": 5,
    "enable_emotional_check": True,
    "show_transparency_by_default": True,
    "enable_bias_warning": True
}

# ========== 偏见检测配置 ==========
BIAS_DETECTION = {
    "enabled": True,
    "threshold": 0.3,
    "check_demographic_bias": True,
    "check_language_bias": True,
    "check_scenario_bias": True
}

# ========== 透明度配置 ==========
TRANSPARENCY = {
    "show_decision_factors": True,
    "show_confidence_score": True,
    "show_counterfactual": True,
    "show_alternative_scenarios": True
}
