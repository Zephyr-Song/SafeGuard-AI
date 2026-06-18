"""
生成PDF说明文档
"""

import os
import platform
from datetime import datetime

# 创建HTML文件，然后转换为PDF
html_content = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>SafeGuard AI 使用说明</title>
    <style>
        @page { size: A4; margin: 2cm; }
        body { 
            font-family: "Microsoft YaHei", "SimHei", sans-serif;
            line-height: 1.8; 
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        h1 { 
            color: #2563eb; 
            text-align: center;
            border-bottom: 3px solid #2563eb;
            padding-bottom: 10px;
        }
        h2 { 
            color: #1d4ed8; 
            margin-top: 30px;
            border-left: 4px solid #2563eb;
            padding-left: 10px;
        }
        h3 { color: #3b82f6; }
        .highlight {
            background: linear-gradient(135deg, #dbeafe, #bfdbfe);
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
        }
        .warning {
            background: linear-gradient(135deg, #fef3c7, #fde68a);
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #f59e0b;
            margin: 15px 0;
        }
        .success {
            background: linear-gradient(135deg, #d1fae5, #a7f3d0);
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #10b981;
            margin: 15px 0;
        }
        code {
            background: #f3f4f6;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: Consolas, monospace;
        }
        pre {
            background: #1f2937;
            color: #e5e7eb;
            padding: 15px;
            border-radius: 8px;
            overflow-x: auto;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }
        th, td {
            border: 1px solid #e5e7eb;
            padding: 10px;
            text-align: left;
        }
        th {
            background: #2563eb;
            color: white;
        }
        tr:nth-child(even) {
            background: #f9fafb;
        }
        .icon { font-size: 1.2em; margin-right: 5px; }
        .footer {
            margin-top: 50px;
            text-align: center;
            color: #6b7280;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <h1>🛡️ SafeGuard AI 使用说明</h1>
    <p style="text-align: center; color: #6b7280;">安全教育与AI伦理学习平台</p>
    
    <div class="highlight">
        <strong>📋 项目简介</strong><br>
        SafeGuard AI 是基于Fraud-R1改进的安全教育平台，帮助用户学习识别网络诈骗，
        同时理解AI决策的透明度与偏见。
    </div>

    <h2>🚀 快速开始</h2>
    
    <h3>方法一：直接运行（推荐）</h3>
    <div class="success">
        <strong>步骤1：打开PowerShell终端</strong>
    </div>
    <pre>cd C:\Users\song\.qclaw\workspace\SafeGuard-AI</pre>
    
    <div class="success">
        <strong>步骤2：安装依赖</strong>
    </div>
    <pre>pip install flask requests python-dotenv</pre>
    
    <div class="success">
        <strong>步骤3：运行应用</strong>
    </div>
    <pre>python app.py</pre>
    
    <div class="success">
        <strong>步骤4：访问应用</strong>
    </div>
    <p>打开浏览器，访问：<code>http://localhost:5000</code></p>

    <h3>方法二：使用虚拟环境</h3>
    <pre># 1. 进入项目目录
cd C:\Users\song\.qclaw\workspace\SafeGuard-AI

# 2. 创建虚拟环境
python -m venv venv

# 3. 激活虚拟环境
venv\\Scripts\\activate

# 4. 安装依赖
pip install flask requests python-dotenv

# 5. 运行应用
python app.py</pre>

    <h2>📁 项目结构</h2>
    <table>
        <tr>
            <th>文件/文件夹</th>
            <th>说明</th>
        </tr>
        <tr>
            <td><code>app.py</code></td>
            <td>主应用入口，Flask后端</td>
        </tr>
        <tr>
            <td><code>config.py</code></td>
            <td>配置文件</td>
        </tr>
        <tr>
            <td><code>modules/</code></td>
            <td>核心功能模块</td>
        </tr>
        <tr>
            <td><code>templates/</code></td>
            <td>前端HTML模板</td>
        </tr>
        <tr>
            <td><code>README.md</code></td>
            <td>项目说明文档</td>
        </tr>
    </table>

    <h2>🎮 使用指南</h2>
    
    <h3>1. 选择学习场景</h3>
    <p>平台提供5种诈骗类型学习：</p>
    <ul>
        <li><span class="icon">🎭</span>虚假服务 - 伪装成正规服务机构</li>
        <li><span class="icon">👤</span>身份冒充 - 冒充熟人或官方</li>
        <li><span class="icon">🎣</span>钓鱼诈骗 - 虚假链接窃取信息</li>
        <li><span class="icon">💼</span>虚假招聘 - 高薪招聘骗局</li>
        <li><span class="icon">💕</span>网恋诈骗 - 感情诈骗</li>
    </ul>

    <h3>2. 互动学习流程</h3>
    <div class="highlight">
        <strong>学习步骤：</strong>
        <ol>
            <li>点击选择一种诈骗类型</li>
            <li>点击"开始学习"按钮</li>
            <li>阅读模拟的诈骗消息</li>
            <li>在文本框中输入你的判断</li>
            <li>点击"提交回复"查看分析</li>
            <li>查看AI透明度和反馈</li>
        </ol>
    </div>

    <h3>3. 查看透明度分析</h3>
    <p>在"🔍 透明度仪表板"标签页，你可以看到：</p>
    <ul>
        <li>AI决策因素分析（权重、置信度）</li>
        <li>偏见检测结果</li>
        <li>反事实推理场景</li>
    </ul>

    <h3>4. 获取帮助</h3>
    <p>在学习过程中，可以点击"💡 获取提示"按钮获得线索。</p>

    <h2>⚠️ 注意事项</h2>
    
    <div class="warning">
        <strong>内容警告：</strong><br>
        平台包含模拟诈骗场景，旨在教育目的。所有内容均为学习材料，
        不会对您造成实际伤害。如感到不适，请随时停止学习。
    </div>

    <div class="warning">
        <strong>安全提示：</strong><br>
        <ul>
            <li>学习场景中的联系方式、链接均为虚构，请勿真实联系或点击</li>
            <li>平台仅在本地运行，不会收集您的个人信息</li>
            <li>建议在学习后与家人朋友分享所学知识</li>
        </ul>
    </div>

    <h2>🔧 故障排除</h2>
    
    <table>
        <tr>
            <th>问题</th>
            <th>解决方案</th>
        </tr>
        <tr>
            <td>端口5000被占用</td>
            <td>修改app.py最后一行：<code>app.run(port=5001)</code></td>
        </tr>
        <tr>
            <td>缺少依赖包</td>
            <td>运行：<code>pip install flask requests python-dotenv</code></td>
        </tr>
        <tr>
            <td>页面显示异常</td>
            <td>清除浏览器缓存，或尝试使用Chrome/Firefox</td>
        </tr>
        <tr>
            <td>Python版本过低</td>
            <td>需要Python 3.8或更高版本</td>
        </tr>
    </table>

    <h2>📊 核心功能</h2>
    
    <h3>1. 互动式学习</h3>
    <p>通过模拟真实诈骗场景，让用户在实践中学习识别技巧。</p>

    <h3>2. 透明度仪表板</h3>
    <p>展示AI如何分析风险，包括决策因素、权重和置信度。</p>

    <h3>3. 偏见检测</h3>
    <p>识别和分析AI系统中的潜在偏见，提升AI伦理意识。</p>

    <h3>4. 反事实推理</h3>
    <p>探索"如果...会怎样"的场景，培养批判性思维。</p>

    <h3>5. 安全守护</h3>
    <p>创伤知情的安全检查，保护学习者情绪健康。</p>

    <h2>🎯 学习目标</h2>
    
    <div class="success">
        完成学习后，您将能够：
        <ul>
            <li>✅ 识别5种常见网络诈骗类型</li>
            <li>✅ 理解AI如何分析和判断风险</li>
            <li>✅ 意识到AI系统中的潜在偏见</li>
            <li>✅ 培养批判性思维和风险意识</li>
            <li>✅ 保护自己和家人免受诈骗</li>
        </ul>
    </div>

    <h2>📞 技术支持</h2>
    
    <p>如遇到问题，请检查：</p>
    <ol>
        <li>Python版本是否为3.8+</li>
        <li>是否已安装所有依赖包</li>
        <li>端口5000是否被其他程序占用</li>
        <li>防火墙是否阻止了本地访问</li>
    </ol>

    <h2>📚 相关文档</h2>
    
    <ul>
        <li><code>README.md</code> - 项目简介</li>
        <li><code>PROJECT_REPORT.md</code> - 详细技术报告</li>
        <li><code>DEMO_DOCUMENTATION.md</code> - 功能演示文档</li>
        <li><code>PROJECT_SUMMARY.md</code> - 项目总结</li>
    </ul>

    <div class="footer">
        <p>SafeGuard AI - 基于Fraud-R1改进的安全教育平台</p>
        <p>生成时间：''' + datetime.now().strftime('%Y年%m月%d日') + '''</p>
        <p>仅供学习研究使用</p>
    </div>
</body>
</html>'''

# 保存HTML文件
output_dir = "C:/Users/song/.qclaw/workspace/SafeGuard-AI"
html_path = os.path.join(output_dir, "使用说明.html")

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"HTML说明文档已生成: {html_path}")
print("\n您可以通过以下方式查看：")
print("1. 直接用浏览器打开HTML文件")
print("2. 在浏览器中按Ctrl+P打印为PDF")
print("3. 使用在线HTML转PDF工具转换")

# 尝试使用weasyprint生成PDF（如果已安装）
try:
    from weasyprint import HTML
    pdf_path = os.path.join(output_dir, "SafeGuard_AI_使用说明.pdf")
    HTML(html_path).write_pdf(pdf_path)
    print(f"\nPDF文档已生成: {pdf_path}")
except ImportError:
    print("\n注意：未安装weasyprint库，已生成HTML版本")
    print("要生成PDF，请安装: pip install weasyprint")
    print("或使用浏览器打印功能保存为PDF")

print(f"\n文件位置: {output_dir}")
