# SafeGuard AI - 安全教育与AI伦理学习平台

基于Fraud-R1改进的AI安全教育系统，专注于：
1. **反欺诈教育** - 帮助用户识别和防范网络诈骗
2. **AI伦理学习** - 理解AI决策的偏见与透明度
3. **互动式学习** - 通过角色扮演和模拟提升安全意识

## 核心创新点

### 1. 教育模式转换
- 从"攻击测试"转变为"学习体验"
- 引入渐进式学习路径
- 实时反馈与解释系统

### 2. 透明度仪表板
- 展示AI决策过程
- 偏见检测与可视化
- 反事实推理展示

### 3. 安全干预机制
- 内容 distress 检测
- 创伤知情安全提示
- 学习者情绪状态监控

## 项目结构

```
SafeGuard-AI/
├── app.py                 # 主应用入口
├── config.py              # 配置文件
├── modules/
│   ├── __init__.py
│   ├── education_engine.py    # 教育内容生成引擎
│   ├── scenario_simulator.py  # 场景模拟器
│   ├── bias_detector.py       # 偏见检测器
│   ├── transparency_dashboard.py  # 透明度仪表板
│   ├── safety_guardian.py     # 安全守护模块
│   └── learning_tracker.py    # 学习进度追踪
├── data/
│   ├── scenarios/         # 教育场景数据
│   └── feedback/          # 学习反馈数据
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── templates/
│   └── index.html
└── reports/               # 生成的报告
```

## 安装与运行

```bash
# 安装依赖
pip install -r requirements.txt

# 运行应用
python app.py

# 访问 http://localhost:5000
```

## 使用说明

1. **选择学习模式**：初学者/进阶/专家
2. **选择场景类型**：诈骗服务/冒充/钓鱼/虚假招聘/网恋
3. **开始互动学习**：与AI模拟的诈骗场景互动
4. **查看透明度分析**：了解AI如何判断风险
5. **获取学习报告**：查看学习进度和建议
