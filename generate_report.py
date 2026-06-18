"""
生成项目报告PDF
"""

import os
import sys

# 注册中文字体
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

def register_chinese_font():
    """注册中文字体"""
    font_paths = [
        ("C:/Windows/Fonts/msyh.ttc", "MicrosoftYaHei"),
        ("C:/Windows/Fonts/simhei.ttf", "SimHei"),
        ("C:/Windows/Fonts/simsun.ttc", "SimSun"),
    ]
    
    for font_path, font_name in font_paths:
        if os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont(font_name, font_path))
                return font_name
            except:
                continue
    
    return "Helvetica"

def create_report():
    """创建PDF报告"""
    # 注册字体
    cn_font = register_chinese_font()
    
    # 创建PDF
    output_path = "C:/Users/song/.qclaw/workspace/SafeGuard-AI/SafeGuard_AI_Project_Report.pdf"
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    # 样式
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=cn_font,
        fontSize=24,
        textColor=colors.HexColor('#2563eb'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading1_style = ParagraphStyle(
        'CustomHeading1',
        parent=styles['Heading1'],
        fontName=cn_font,
        fontSize=18,
        textColor=colors.HexColor('#1d4ed8'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    heading2_style = ParagraphStyle(
        'CustomHeading2',
        parent=styles['Heading2'],
        fontName=cn_font,
        fontSize=14,
        textColor=colors.HexColor('#2563eb'),
        spaceAfter=10,
        spaceBefore=10
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontName=cn_font,
        fontSize=11,
        leading=18,
        alignment=TA_LEFT
    )
    
    # 构建内容
    story = []
    
    # 封面
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("SafeGuard AI", title_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("安全教育与AI伦理学习平台", title_style))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("基于Fraud-R1改进的项目报告", body_style))
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("2025年3月", body_style))
    story.append(PageBreak())
    
    # 目录
    story.append(Paragraph("目录", heading1_style))
    story.append(Spacer(1, 0.2*inch))
    
    toc_items = [
        "1. 项目概述",
        "2. 系统架构",
        "3. 核心功能演示",
        "4. 技术创新",
        "5. 数据生成与分析",
        "6. 应用场景",
        "7. 伦理考量",
        "8. 结论与展望"
    ]
    
    for item in toc_items:
        story.append(Paragraph(item, body_style))
        story.append(Spacer(1, 0.1*inch))
    
    story.append(PageBreak())
    
    # 第1章
    story.append(Paragraph("1. 项目概述", heading1_style))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("1.1 项目背景", heading2_style))
    story.append(Paragraph(
        "本项目基于Fraud-R1（一个多轮次LLM反欺诈基准测试框架）进行改进，"
        "将其从攻击测试工具转变为安全教育与AI伦理学习平台。",
        body_style
    ))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("1.2 项目目标", heading2_style))
    story.append(Paragraph("• 教育目标：帮助用户识别和防范网络诈骗", body_style))
    story.append(Paragraph("• 伦理目标：理解AI决策的透明度、偏见与公平性", body_style))
    story.append(Paragraph("• 技术目标：实现一个安全、可解释、负责任的AI教育系统", body_style))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("1.3 核心创新", heading2_style))
    story.append(Paragraph("1. 模式转换：从攻击测试到教育学习", body_style))
    story.append(Paragraph("2. 透明度仪表板：展示AI决策过程", body_style))
    story.append(Paragraph("3. 偏见检测：识别和分析AI系统中的潜在偏见", body_style))
    story.append(Paragraph("4. 反事实推理：探索如果...会怎样的场景", body_style))
    story.append(Paragraph("5. 安全守护：创伤知情的安全检查机制", body_style))
    
    story.append(PageBreak())
    
    # 第2章
    story.append(Paragraph("2. 系统架构", heading1_style))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("2.1 核心模块", heading2_style))
    story.append(Spacer(1, 0.1*inch))
    
    # 模块表格
    module_data = [
        ["模块名称", "功能描述", "核心特点"],
        ["教育引擎", "生成个性化安全教育内容", "多阶段学习、自适应难度"],
        ["场景模拟器", "创建互动式学习场景", "5种诈骗类型、多轮对话"],
        ["透明度仪表板", "展示AI决策过程", "决策可视化、偏见检测"],
        ["安全守护", "内容安全检查", "情绪监控、创伤知情"],
        ["学习追踪", "追踪学习进度", "成就系统、进度可视化"]
    ]
    
    module_table = Table(module_data, colWidths=[1.5*inch, 2.2*inch, 2.2*inch])
    module_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), cn_font),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), cn_font),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    story.append(module_table)
    story.append(PageBreak())
    
    # 第3章
    story.append(Paragraph("3. 核心功能演示", heading1_style))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("3.1 互动学习流程", heading2_style))
    story.append(Paragraph("步骤1：选择学习场景（5种诈骗类型）", body_style))
    story.append(Paragraph("步骤2：场景模拟（接收模拟诈骗信息）", body_style))
    story.append(Paragraph("步骤3：用户响应与分析（AI评估用户判断）", body_style))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("3.2 透明度分析示例", heading2_style))
    story.append(Paragraph(
        "AI系统展示决策因素分析，包括风险指标、紧急性分析、发送者验证等，"
        "每个因素都有相应的权重和置信度。",
        body_style
    ))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("3.3 反事实推理", heading2_style))
    story.append(Paragraph(
        "系统提供反事实场景分析，例如：如果发送者可以通过官方渠道验证，"
        "风险等级将如何变化。这帮助用户理解决策的边界条件。",
        body_style
    ))
    
    story.append(PageBreak())
    
    # 第4章
    story.append(Paragraph("4. 技术创新", heading1_style))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("4.1 与Fraud-R1的对比", heading2_style))
    story.append(Spacer(1, 0.1*inch))
    
    compare_data = [
        ["特性", "Fraud-R1", "SafeGuard AI"],
        ["主要目标", "测试LLM脆弱性", "教育用户识别诈骗"],
        ["交互模式", "攻击-防御", "学习-反馈"],
        ["透明度", "黑盒测试", "白盒解释"],
        ["安全性", "无保护", "创伤知情"],
        ["偏见关注", "无", "有"],
        ["反事实", "无", "有"]
    ]
    
    compare_table = Table(compare_data, colWidths=[1.8*inch, 2*inch, 2.2*inch])
    compare_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7c3aed')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), cn_font),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lavender),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), cn_font),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    story.append(compare_table)
    story.append(PageBreak())
    
    # 第5章
    story.append(Paragraph("5. 数据生成与分析", heading1_style))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("5.1 生成的数据类型", heading2_style))
    story.append(Paragraph("• 学习场景数据：包含诈骗类型、风险点、学习要点", body_style))
    story.append(Paragraph("• 用户响应数据：用户判断、识别准确率、学习进度", body_style))
    story.append(Paragraph("• 透明度分析数据：决策因素、偏见检测、反事实推理", body_style))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("5.2 数据分析能力", heading2_style))
    story.append(Paragraph("• 学习效果分析：识别准确率统计、薄弱环节识别", body_style))
    story.append(Paragraph("• 公平性分析：不同群体学习效果对比、偏见影响评估", body_style))
    story.append(Paragraph("• 系统性能分析：响应时间、决策准确性、用户满意度", body_style))
    
    story.append(PageBreak())
    
    # 第6章
    story.append(Paragraph("6. 应用场景", heading1_style))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("6.1 个人用户", heading2_style))
    story.append(Paragraph("提升防诈骗意识，学习识别技巧，了解AI决策过程", body_style))
    story.append(Spacer(1, 0.1*inch))
    
    story.append(Paragraph("6.2 教育机构", heading2_style))
    story.append(Paragraph("网络安全课程、数字素养培训、AI伦理教育", body_style))
    story.append(Spacer(1, 0.1*inch))
    
    story.append(Paragraph("6.3 企业培训", heading2_style))
    story.append(Paragraph("员工安全意识培训、反欺诈技能培训、合规培训", body_style))
    story.append(Spacer(1, 0.1*inch))
    
    story.append(Paragraph("6.4 公共教育", heading2_style))
    story.append(Paragraph("社区安全教育、老年人防诈骗、青少年网络素养", body_style))
    
    story.append(PageBreak())
    
    # 第7章
    story.append(Paragraph("7. 伦理考量", heading1_style))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("7.1 安全设计原则", heading2_style))
    story.append(Paragraph("• 创伤知情：前置内容警告、情绪状态监控、分级干预", body_style))
    story.append(Paragraph("• 透明度：决策过程可视化、偏见检测公开、置信度说明", body_style))
    story.append(Paragraph("• 公平性：多语言支持、多场景覆盖、偏见主动检测", body_style))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("7.2 隐私保护", heading2_style))
    story.append(Paragraph("本地数据存储、匿名化处理、最小数据收集、用户数据控制", body_style))
    
    story.append(PageBreak())
    
    # 第8章
    story.append(Paragraph("8. 结论与展望", heading1_style))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph(
        "SafeGuard AI成功将Fraud-R1从攻击测试工具转变为安全教育平台，实现了：",
        body_style
    ))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("1. 教育价值：提供有效的反诈骗教育", body_style))
    story.append(Paragraph("2. 技术创新：实现透明度、偏见检测、反事实推理", body_style))
    story.append(Paragraph("3. 安全设计：创伤知情的安全保护机制", body_style))
    story.append(Paragraph("4. 伦理责任：负责任的AI应用", body_style))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph(
        "本项目展示了如何将AI安全技术转化为社会教育工具，为AI伦理教育提供了新的范式。",
        body_style
    ))
    
    # 生成PDF
    doc.build(story)
    print(f"PDF报告已生成: {output_path}")
    return output_path

if __name__ == "__main__":
    create_report()
