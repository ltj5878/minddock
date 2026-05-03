import json
from datetime import datetime, timedelta
from openai import AsyncOpenAI
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.config import settings
from app.models import Note, Project, Task

async def generate_weekly_review(db: Session) -> str:
    if not settings.openai_api_key:
        return "请先配置 OpenAI API Key 以生成 AI 复盘总结。"
    
    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)
    
    notes = db.scalars(select(Note).where(Note.created_at >= week_ago)).all()
    projects = db.scalars(select(Project).where(Project.status == "active")).all()
    tasks = db.scalars(select(Task).where(Task.status == "todo")).all()
    
    notes_summary = "\n".join([f"- {n.title}: {n.summary or n.content[:100]}" for n in notes[:15]])
    projects_summary = "\n".join([f"- {p.name}: {p.goal}" for p in projects])
    
    prompt = (
        f"时间范围：过去 7 天\n\n"
        f"新增笔记：\n{notes_summary}\n\n"
        f"活跃项目：\n{projects_summary}\n\n"
        f"待办任务数：{len(tasks)}\n\n"
        "请为我生成一份本周复盘报告。包括：\n"
        "1. 本周活动概览\n"
        "2. 关键主题分析\n"
        "3. 下周行动建议\n"
        "使用 Markdown 格式，语言为中文。"
    )
    
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    response = await client.chat.completions.create(
        model=settings.openai_chat_model,
        messages=[
            {"role": "system", "content": "你是一个专业的个人知识管理和生产力教练。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4
    )
    
    return response.choices[0].message.content or "未能生成总结。"
