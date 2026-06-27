"""
主应用入口
SafeGuard AI - 安全教育与AI伦理学习平台
"""

import os
import sys
import json
from datetime import datetime
from flask import Flask, render_template, jsonify, request, session, Response, redirect
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()
load_dotenv(".env.local", override=False)

# 添加模块路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.education_engine import EducationEngine, LearningStage
from modules.scenario_simulator import ScenarioSimulator, SimulationScenario
from modules.transparency_dashboard import TransparencyDashboard
from modules.safety_guardian import SafetyGuardian, SafetyCheck
from modules.learning_tracker import LearningTracker
from modules.ai_analyzer import AIAnalyzer
from modules.rehearsal_engine import RehearsalEngine
from modules.reflection_dashboard import ReflectionDashboard
from modules.rehearsal_logger import RehearsalLogger
from modules.encounter_api import encounter_api
from config import FRAUD_CATEGORIES, DIFFICULTY_LEVELS, SAFETY_CONFIG, ACTIVE_MODEL

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))
app.secret_key = os.getenv("FLASK_SECRET_KEY") or os.urandom(24)
app.register_blueprint(encounter_api)


@app.before_request
def protect_public_demo():
    """Optional HTTP Basic Auth for public demos on Render."""
    if os.getenv("ENABLE_DEMO_AUTH", "0") != "1":
        return None

    demo_password = os.getenv("SAFEBARS_DEMO_PASSWORD")
    if not demo_password or request.path == "/healthz":
        return None

    demo_user = os.getenv("SAFEBARS_DEMO_USER", "safebars")
    auth = request.authorization
    if auth and auth.username == demo_user and auth.password == demo_password:
        return None

    return Response(
        "Authentication required",
        401,
        {"WWW-Authenticate": 'Basic realm="SafeBARS Demo"'},
    )


@app.route("/healthz")
def healthz():
    return jsonify({"success": True, "service": "safebars"})

# 初始化组件
education_engine = EducationEngine()
scenario_simulator = ScenarioSimulator()
transparency_dashboard = TransparencyDashboard()
safety_guardian = SafetyGuardian()
learning_tracker = LearningTracker()
rehearsal_engine = RehearsalEngine()
reflection_dashboard = ReflectionDashboard()
rehearsal_logger = RehearsalLogger()

# 初始化AI分析器
ai_analyzer = AIAnalyzer(model=ACTIVE_MODEL)

@app.route('/')
def index():
    """主页"""
    return redirect('/safebars')

@app.route('/legacy')
def legacy_index():
    """Legacy SafeGuard AI page."""
    return render_template('index.html')

@app.route('/test')
def test_page():
    """测试页面"""
    return render_template('test.html')

@app.route('/diagnostic')
def diagnostic_page():
    """诊断页面"""
    return render_template('diagnostic.html')

@app.route('/safebars')
def safebars_page():
    """SafeBARS研究者预演界面"""
    return render_template('safebars_v2.html', study_mode=False)

@app.route('/safebars/study')
def safebars_study_page():
    """SafeBARS参与者研究模式界面"""
    return render_template('safebars_v2.html', study_mode=True)

@app.route('/safebars/v1')
def safebars_v1_page():
    """Preserved v1 synthetic stakeholder rehearsal interface."""
    return render_template('safebars.html', study_mode=False)

@app.route('/safebars/v1/study')
def safebars_v1_study_page():
    """Preserved v1 study interface."""
    return render_template('safebars.html', study_mode=True)

@app.route('/safebars/brief')
def safebars_brief_page():
    """SafeBARS导师展示摘要页"""
    return render_template('safebars_brief.html')

@app.route('/api/categories')
def get_categories():
    """获取诈骗类别"""
    return jsonify({
        "success": True,
        "categories": FRAUD_CATEGORIES
    })

@app.route('/api/start-learning', methods=['POST'])
def start_learning():
    """开始学习"""
    data = request.json
    user_id = data.get('user_id', 'anonymous')
    category = data.get('category', 'fraudulent_service')
    difficulty = data.get('difficulty', 'beginner')
    
    # 设置用户ID
    session['user_id'] = user_id
    session['difficulty'] = difficulty
    
    # 安全检查 - 前置警告
    warning = safety_guardian.pre_content_warning(category)
    
    # 创建模拟场景
    try:
        scenario = scenario_simulator.create_simulation(category, user_id)
        
        # 开始学习会话
        learning_tracker.start_session(user_id, category, scenario.id)
        
        return jsonify({
            "success": True,
            "scenario": {
                "id": scenario.id,
                "title": scenario.title,
                "description": scenario.description,
                "category": scenario.category,
                "total_rounds": len(scenario.rounds)
            },
            "warning": warning,
            "current_round": scenario_simulator.get_current_round(user_id).__dict__ if scenario_simulator.get_current_round(user_id) else None
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/api/submit-response', methods=['POST'])
def submit_response():
    """提交响应"""
    data = request.json
    user_id = session.get('user_id', 'anonymous')
    response = data.get('response', '')
    
    # 安全检查
    safety_check = safety_guardian.check_content_safety(response, context="learning")
    
    if safety_check.action_required.value in ['stop', 'escalate']:
        return jsonify({
            "success": False,
            "safety_alert": {
                "message": safety_check.message,
                "resources": safety_check.resources,
                "level": safety_check.distress_level.value
            }
        })
    
    # 处理响应
    result = scenario_simulator.process_response(user_id, response)
    
    if result.get('error'):
        return jsonify({
            "success": False,
            "error": result['error']
        })
    
    # 获取当前场景信息用于透明度分析
    sim_data = scenario_simulator.active_simulations.get(user_id)
    if sim_data:
        current_round = sim_data['current_round'] - 1
        if current_round >= 0 and current_round < len(sim_data['scenario'].rounds):
            round_content = sim_data['scenario'].rounds[current_round].content
            category = sim_data['scenario'].category
            
            # 生成透明度分析
            transparency_analysis = transparency_dashboard.analyze_decision(
                round_content, response, category
            )
        else:
            transparency_analysis = None
    else:
        transparency_analysis = None
    
    # 检查是否完成
    if result['is_complete']:
        # 获取总结
        summary = scenario_simulator.get_simulation_summary(user_id)
        
        # 结束学习会话
        learning_tracker.end_session(
            user_id, 
            summary.get('average_safety_score', 0),
            summary
        )
        
        # 清理模拟
        scenario_simulator.end_simulation(user_id)
        
        return jsonify({
            "success": True,
            "completed": True,
            "summary": summary,
            "transparency_analysis": transparency_analysis,
            "safety_check": {
                "message": safety_check.message,
                "resources": safety_check.resources
            } if safety_check.distress_detected else None
        })
    
    return jsonify({
        "success": True,
        "completed": False,
        "analysis": result['analysis'],
        "next_round": result['next_round'].__dict__ if result['next_round'] else None,
        "progress": result['progress'],
        "transparency_analysis": transparency_analysis,
        "safety_check": {
            "message": safety_check.message,
            "resources": safety_check.resources
        } if safety_check.distress_detected else None
    })

@app.route('/api/get-hint', methods=['POST'])
def get_hint():
    """获取提示"""
    user_id = session.get('user_id', 'anonymous')
    hint = scenario_simulator.get_hint(user_id)
    
    return jsonify({
        "success": True,
        "hint": hint
    })

@app.route('/api/transparency-analysis', methods=['POST'])
def get_transparency_analysis():
    """获取透明度分析"""
    data = request.json
    content = data.get('content', '')
    response = data.get('response', '')
    category = data.get('category', '')
    
    analysis = transparency_dashboard.analyze_decision(content, response, category)
    
    return jsonify({
        "success": True,
        "analysis": analysis
    })

@app.route('/api/fairness-analysis')
def get_fairness_analysis():
    """获取公平性分析"""
    analysis = transparency_dashboard.generate_fairness_analysis()
    
    return jsonify({
        "success": True,
        "analysis": analysis
    })

@app.route('/api/progress')
def get_progress():
    """获取学习进度"""
    user_id = session.get('user_id', 'anonymous')
    progress = learning_tracker.get_progress_summary(user_id)
    
    return jsonify({
        "success": True,
        "progress": progress
    })

@app.route('/api/learning-report')
def get_learning_report():
    """获取学习报告"""
    user_id = session.get('user_id', 'anonymous')
    report = learning_tracker.generate_learning_report(user_id)
    
    return jsonify({
        "success": True,
        "report": report
    })

@app.route('/api/safety-check', methods=['POST'])
def check_safety():
    """安全检查"""
    data = request.json
    content = data.get('content', '')
    context = data.get('context', 'general')
    
    safety_check = safety_guardian.check_content_safety(content, context)
    
    return jsonify({
        "success": True,
        "safety_check": {
            "is_safe": safety_check.is_safe,
            "distress_detected": safety_check.distress_detected,
            "distress_level": safety_check.distress_level.value,
            "action_required": safety_check.action_required.value,
            "message": safety_check.message,
            "resources": safety_check.resources
        }
    })

@app.route('/api/safebars/options')
def safebars_options():
    """获取SafeBARS角色和profile预设"""
    return jsonify({
        "success": True,
        "roles": rehearsal_engine.list_roles(),
        "presets": rehearsal_engine.list_presets(),
        "llm_configured": rehearsal_engine.llm_client.is_configured(),
        "llm_providers": rehearsal_engine.list_llm_providers()
    })

@app.route('/api/safebars/start', methods=['POST'])
def safebars_start():
    """开始SafeBARS预演会话"""
    try:
        data = request.json or {}
        rehearsal_session = rehearsal_engine.start_session(data)
        return jsonify({
            "success": True,
            "session": rehearsal_session.to_dict()
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/safebars/message', methods=['POST'])
def safebars_message():
    """向synthetic stakeholder发送消息"""
    data = request.json or {}
    session_id = data.get("session_id", "")
    message = data.get("message", "")
    if not session_id or not message:
        return jsonify({
            "success": False,
            "error": "Missing session_id or message"
        }), 400

    result = rehearsal_engine.add_message(session_id, message)
    if not result:
        return jsonify({
            "success": False,
            "error": "Session not found"
        }), 404

    return jsonify({
        "success": True,
        **result
    })

@app.route('/api/safebars/compare', methods=['POST'])
def safebars_compare():
    """Compare template and configured LLM providers for one rehearsal prompt."""
    data = request.json or {}
    session_id = data.get("session_id", "")
    message = data.get("message", "")
    if not session_id or not message:
        return jsonify({
            "success": False,
            "error": "Missing session_id or message"
        }), 400

    try:
        result = rehearsal_engine.compare_responses(session_id, message)
        if not result:
            return jsonify({
                "success": False,
                "error": "Session not found"
            }), 404
    except Exception as exc:
        return jsonify({
            "success": False,
            "error": f"Comparison failed before providers could return: {str(exc)[:500]}"
        }), 500

    return jsonify({
        "success": True,
        **result
    })

@app.route('/api/safebars/export-comparison', methods=['POST'])
def safebars_export_comparison():
    """Export a provider comparison result."""
    data = request.json or {}
    session_id = data.get("session_id", "")
    message = data.get("message", "")
    responses = data.get("responses", [])
    comparison_summary = data.get("comparison_summary", {})
    if not session_id or not message or not responses:
        return jsonify({
            "success": False,
            "error": "Missing session_id, message, or responses"
        }), 400

    paths = rehearsal_logger.export_comparison({
        "session_id": session_id,
        "message": message,
        "responses": responses,
        "comparison_summary": comparison_summary,
    })
    return jsonify({
        "success": True,
        **paths
    })

@app.route('/api/safebars/reflection', methods=['POST'])
def safebars_reflection():
    """生成研究计划反思报告"""
    data = request.json or {}
    session_id = data.get("session_id", "")
    rehearsal_session = rehearsal_engine.get_session(session_id)
    if not rehearsal_session:
        return jsonify({
            "success": False,
            "error": "Session not found"
        }), 404

    session_data = rehearsal_session.to_dict()
    report = reflection_dashboard.generate_report(session_data).to_dict()
    report["llm_dynamic_reflection"] = build_llm_dynamic_reflection(session_data, report)
    return jsonify({
        "success": True,
        "report": report
    })


def build_llm_dynamic_reflection(session_data, structured_report):
    """Use the configured LLM to summarize this exact rehearsal session."""
    llm_client = rehearsal_engine.llm_client
    if not llm_client.is_configured():
        return ["LLM dynamic reflection is unavailable because no LLM provider is configured."]

    plan = session_data.get("research_plan", {})
    stakeholder = session_data.get("stakeholder", {})
    turns = session_data.get("turns", [])
    transcript_lines = []
    for turn in turns[-10:]:
        speaker = turn.get("speaker", "unknown")
        text = turn.get("text", "").replace("\n", " ").strip()
        metadata = turn.get("metadata", {})
        signal = metadata.get("rehearsal_signal", "")
        flags = ", ".join(metadata.get("safety_flags", []))
        if signal or flags:
            transcript_lines.append(f"{speaker}: {text} [signal={signal}; flags={flags}]")
        else:
            transcript_lines.append(f"{speaker}: {text}")

    messages = [
        {
            "role": "system",
            "content": (
                "You are SafeBARS reflection assistant. Summarize only this rehearsal session. "
                "Do not claim to represent real participants, older adults, victims, or communities. "
                "Treat synthetic stakeholder output as rehearsal evidence about the research plan, not participant evidence. "
                "Be concrete, concise, and action-oriented."
            ),
        },
        {
            "role": "user",
            "content": (
                "Generate a dynamic reflection for this SafeBARS session.\n\n"
                "Return exactly 4 bullets, each under 35 words:\n"
                "1. Most session-specific risk surfaced.\n"
                "2. Concrete wording or procedure change.\n"
                "3. What the researcher should verify with real stakeholders.\n"
                "4. One caution about trusting this synthetic rehearsal.\n\n"
                f"Research plan title: {plan.get('title', '')}\n"
                f"Goal: {plan.get('goal', '')}\n"
                f"Target community: {plan.get('target_community', '')}\n"
                f"Method: {plan.get('planned_method', '')}\n"
                f"Draft materials: {plan.get('draft_materials', '')}\n"
                f"Known risks: {plan.get('known_risks', '')}\n"
                f"Stakeholder role: {stakeholder.get('display_name', stakeholder.get('role', ''))}\n\n"
                "Recent rehearsal transcript:\n"
                + "\n".join(transcript_lines)
                + "\n\nStructured fallback report cues:\n"
                f"Takeaways: {structured_report.get('session_specific_takeaways', [])}\n"
                f"Rewrite suggestions: {structured_report.get('concrete_rewrite_suggestions', [])}\n"
                f"Evidence notes: {structured_report.get('evidence_notes', [])}"
            ),
        },
    ]

    result = llm_client.chat_with_provider_detailed(
        llm_client.active_provider_id,
        messages,
        temperature=0.2,
        timeout=25,
    )
    if not result.get("ok"):
        detail = result.get("error") or result.get("error_type") or "Unknown provider error."
        return [f"LLM dynamic reflection unavailable; structured fallback is shown. Reason: {detail}"]

    bullets = []
    for line in result.get("text", "").splitlines():
        line = line.strip()
        if not line:
            continue
        line = line.lstrip("-*0123456789. ").strip()
        if line:
            bullets.append(line)
    if not bullets:
        bullets = [result.get("text", "").strip()]
    return bullets[:4]

@app.route('/api/safebars/revise', methods=['POST'])
def safebars_revise():
    """保存预演后的研究计划修改"""
    data = request.json or {}
    session_id = data.get("session_id", "")
    revised_plan = data.get("revised_plan", "")
    rehearsal_session = rehearsal_engine.save_revision(session_id, revised_plan)
    if not rehearsal_session:
        return jsonify({
            "success": False,
            "error": "Session not found"
        }), 404
    return jsonify({
        "success": True,
        "session": rehearsal_session.to_dict()
    })

@app.route('/api/safebars/session/<session_id>')
def safebars_session(session_id):
    """获取SafeBARS会话"""
    rehearsal_session = rehearsal_engine.get_session(session_id)
    if not rehearsal_session:
        return jsonify({
            "success": False,
            "error": "Session not found"
        }), 404
    return jsonify({
        "success": True,
        "session": rehearsal_session.to_dict()
    })

@app.route('/api/safebars/export/<session_id>')
def safebars_export(session_id):
    """导出SafeBARS会话"""
    rehearsal_session = rehearsal_engine.get_session(session_id)
    if not rehearsal_session:
        return jsonify({
            "success": False,
            "error": "Session not found"
        }), 404

    session_data = rehearsal_session.to_dict()
    report = reflection_dashboard.generate_report(session_data).to_dict()
    report["llm_dynamic_reflection"] = build_llm_dynamic_reflection(session_data, report)
    json_path = rehearsal_logger.export_json(session_data)
    md_path = rehearsal_logger.export_markdown(session_data, report)
    return jsonify({
        "success": True,
        "json_path": json_path,
        "markdown_path": md_path,
        "report": report
    })

@app.route('/api/health-check')
def health_check():
    """健康检查"""
    user_id = session.get('user_id', 'anonymous')
    health = safety_guardian.check_interaction_health()
    
    return jsonify({
        "success": True,
        "health": health
    })

@app.route('/api/analyze-response', methods=['POST'])
def analyze_response_with_ai():
    """使用AI分析用户回答"""
    try:
        data = request.json
        scenario = data.get('scenario', {})
        user_response = data.get('user_response', '')
        
        if not scenario or not user_response:
            return jsonify({
                "success": False,
                "error": "Missing scenario or user_response"
            }), 400
        
        # 使用AI分析器
        result = ai_analyzer.analyze_response(scenario, user_response)
        
        return jsonify({
            "success": True,
            "score": result.score,
            "percentage": result.percentage,
            "level": result.level,
            "response_type": result.response_type,
            "identified_risks": result.identified_risks,
            "missed_risks": result.missed_risks,
            "feedback": result.feedback,
            "reasoning": result.reasoning
        })
        
    except Exception as e:
        print(f"Error in AI analysis: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/leaderboard')
def get_leaderboard():
    """获取排行榜"""
    leaderboard = learning_tracker.get_leaderboard()
    
    return jsonify({
        "success": True,
        "leaderboard": leaderboard
    })

@app.route('/api/end-session', methods=['POST'])
def end_session():
    """结束会话"""
    user_id = session.get('user_id', 'anonymous')
    
    # 清理模拟
    scenario_simulator.end_simulation(user_id)
    
    return jsonify({
        "success": True,
        "message": "会话已结束"
    })

# 演示模式API
@app.route('/api/demo/scenario')
def get_demo_scenario():
    """获取演示场景"""
    # 返回一个固定的演示场景
    demo_scenario = {
        "id": "demo_001",
        "title": "虚假驾校服务",
        "category": "fraudulent_service",
        "description": "你正在考虑考取驾照，收到一条来自'驾校'的短信。",
        "rounds": [
            {
                "round_number": 1,
                "content": "您好，这里是环城驾校，我们可以代办B1驾照，无需考试，只需支付800元定金和7500元考试费。请转账至账户：6228 4801 2665 3397 775",
                "sender_info": {"name": "李教练", "company": "环城驾校"},
                "hints": ["正规驾校不会承诺'包过'", "要求预付大额费用是危险信号"],
                "red_flags": ["承诺无需考试", "要求预付费用", "个人账户收款"]
            }
        ]
    }
    
    return jsonify({
        "success": True,
        "scenario": demo_scenario
    })

@app.route('/api/demo/analyze', methods=['POST'])
def demo_analyze():
    """演示分析"""
    data = request.json
    user_response = data.get('response', '')
    scenario_content = data.get('scenario_content', '')
    category = data.get('category', 'fraudulent_service')
    
    # 透明度分析
    transparency = transparency_dashboard.analyze_decision(
        scenario_content, user_response, category
    )
    
    # 安全检查
    safety = safety_guardian.check_content_safety(user_response)
    
    # 简单的响应分析
    identified_flags = []
    red_flags = ["承诺无需考试", "要求预付费用", "个人账户收款"]
    
    for flag in red_flags:
        if any(kw in user_response for kw in flag.lower().split()):
            identified_flags.append(flag)
    
    score = len(identified_flags) * 33
    
    return jsonify({
        "success": True,
        "analysis": {
            "score": score,
            "identified_flags": identified_flags,
            "missed_flags": [f for f in red_flags if f not in identified_flags],
            "feedback": "识别了部分风险点，继续努力！" if score > 0 else "建议仔细分析场景中的可疑之处。"
        },
        "transparency": transparency,
        "safety": {
            "distress_detected": safety.distress_detected,
            "message": safety.message
        }
    })

if __name__ == '__main__':
    print("=" * 60)
    print("SafeGuard AI - 安全教育与AI伦理学习平台")
    print("=" * 60)
    print("访问 http://localhost:5000 开始使用")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
