# 🚀 Quick Start Guide - AI Mode

## 第一步：配置API密钥

### 方法1：使用Google Gemini（推荐，有免费额度）

1. 访问 https://makersuite.google.com/app/apikey
2. 创建API密钥
3. 在项目根目录创建 `.env` 文件：

```env
ACTIVE_MODEL=openai
OPENAI_API_KEY=你的API密钥
MOCK_MODE=False
```

### 方法2：使用智谱AI

1. 访问 https://open.bigmodel.cn/
2. 注册并获取API密钥
3. 创建 `.env` 文件：

```env
ACTIVE_MODEL=zhipu
ZHI_KEY=你的API密钥
MOCK_MODE=False
```

## 第二步：安装依赖

```bash
pip install -r requirements.txt
```

## 第三步：运行应用

```bash
python app.py
```

## 第四步：访问网站

打开浏览器访问：http://localhost:5000

## 🧪 测试AI功能

运行测试脚本：

```bash
python test_ai_analyzer.py
```

## ✅ 验证AI模式是否工作

1. 选择一个诈骗场景
2. 输入你的分析
3. 点击"Submit Response"
4. 观察按钮显示"⏳ AI Analyzing..."
5. 等待2-5秒，查看AI给出的分数和反馈

## 🎯 预期效果

### AI模式特征：
- ✅ 按钮显示"AI Analyzing..."
- ✅ 需要等待2-5秒
- ✅ 反馈是AI生成的个性化内容
- ✅ 理解同义词和隐含意思

### 关键词模式特征：
- ⚡ 即时反馈（<1秒）
- ⚡ 使用预设的反馈模板
- ⚡ 只匹配精确关键词

## ⚠️ 常见问题

### Q: 提示"AI analysis unavailable"
A: 检查 `.env` 文件中的API密钥是否正确

### Q: 响应很慢
A: AI分析需要2-5秒，这是正常的

### Q: 如何确认使用的是AI模式？
A: 查看浏览器控制台，会显示API调用日志

## 📞 需要帮助？

查看详细文档：`AI_MODE_README.md`
