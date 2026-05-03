import json
from typing import TypedDict
from openai import AsyncOpenAI
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models import Note, Project, Task

class ProjectInsight(TypedDict):
    summary: str
    next_actions: list[str]
    recommended_tags: list[str]

async def generate_project_insights(
    project: Project, 
    notes: list[Note], 
    pending_tasks: list[Task]
) -> ProjectInsight:
    if not settings.openai_api_key:
        return _generate_heuristic_insights(project, notes, pending_tasks)
    
    try:
        return await _generate_ai_insights(project, notes, pending_tasks)
    except Exception:
        return _generate_heuristic_insights(project, notes, pending_tasks)

async def _generate_ai_insights(
    project: Project, 
    notes: list[Note], 
    pending_tasks: list[Task]
) -> ProjectInsight:
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    
    notes_context = "\n".join([
        f"- {n.title}: {n.summary or n.content[:200]}" 
        for n in notes[:10]
    ])
    tasks_context = "\n".join([f"- {t.title} ({t.status})" for t in pending_tasks])
    
    prompt = (
        f"Project: {project.name}\n"
        f"Goal: {project.goal}\n\n"
        f"Recent Notes:\n{notes_context}\n\n"
        f"Pending Tasks:\n{tasks_context}\n\n"
        "Based on the above, provide a concise summary of the project's current state, "
        "a list of 3-5 next actions, and 3-5 recommended tags. "
        "Respond in JSON format with keys: 'summary', 'next_actions', 'recommended_tags'. "
        "Use Chinese for the response."
    )
    
    response = await client.chat.completions.create(
        model=settings.openai_chat_model,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "You are a project management assistant for MindDock."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
    
    raw = response.choices[0].message.content or "{}"
    data = json.loads(raw)
    return {
        "summary": data.get("summary", ""),
        "next_actions": data.get("next_actions", []),
        "recommended_tags": data.get("recommended_tags", [])
    }

def _generate_heuristic_insights(
    project: Project, 
    notes: list[Note], 
    pending_tasks: list[Task]
) -> ProjectInsight:
    # Fallback to the original logic
    if not notes:
        summary = f"{project.name} 暂无关联笔记，建议记录一些进展。"
    else:
        summary = f"{project.name} 目前有 {len(notes)} 条笔记和 {len(pending_tasks)} 个待办任务。"
    
    next_actions = [t.title for t in pending_tasks[:3]]
    if not next_actions:
        next_actions = ["记录项目当前进展", "梳理后续计划"]
        
    return {
        "summary": summary,
        "next_actions": next_actions,
        "recommended_tags": ["项目推进"]
    }
