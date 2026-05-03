from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Note, Project, Task
from app.services.assistant import generate_project_insights

router = APIRouter()


class ProjectResponse(BaseModel):
    id: str
    name: str
    goal: str
    status: str
    notionProjectPageId: str | None
    createdAt: datetime
    updatedAt: datetime


class TaskResponse(BaseModel):
    id: str
    title: str
    status: str
    priority: str
    dueDate: date | None
    projectId: str | None
    sourceNoteId: str | None
    createdAt: datetime
    updatedAt: datetime


class ProjectsListResponse(BaseModel):
    projects: list[ProjectResponse]
    tasks: list[TaskResponse]


class ProjectAssistantResponse(BaseModel):
    project: ProjectResponse
    noteCount: int
    taskCount: int
    weeklySummary: str
    nextActions: list[str]
    recommendedTags: list[str]
    relatedNoteIds: list[str]


class GenerateTasksResponse(BaseModel):
    created: int
    tasks: list[TaskResponse]


class ProjectCreate(BaseModel):
    name: str
    goal: str | None = None
    status: str = "active"


class ProjectUpdate(BaseModel):
    name: str | None = None
    goal: str | None = None
    status: str | None = None


class TaskCreate(BaseModel):
    title: str
    status: str = "todo"
    priority: str = "medium"
    dueDate: date | None = None
    projectId: str | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    status: str | None = None
    priority: str | None = None
    dueDate: date | None = None


@router.get("", response_model=ProjectsListResponse)
def list_projects(db: Session = Depends(get_db)):
    projects = db.scalars(select(Project)).all()
    tasks = db.scalars(select(Task)).all()
    return ProjectsListResponse(
        projects=[_project_response(project) for project in projects],
        tasks=[_task_response(task) for task in tasks],
    )


@router.post("", response_model=ProjectResponse)
def create_project(req: ProjectCreate, db: Session = Depends(get_db)):
    project = Project(
        name=req.name,
        goal=req.goal or "",
        status=req.status,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return _project_response(project)


@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: str, req: ProjectUpdate, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if req.name is not None:
        project.name = req.name
    if req.goal is not None:
        project.goal = req.goal
    if req.status is not None:
        project.status = req.status
        
    db.commit()
    db.refresh(project)
    return _project_response(project)


@router.delete("/{project_id}")
def delete_project(project_id: str, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
    return {"status": "ok"}


@router.post("/tasks", response_model=TaskResponse)
def create_task(req: TaskCreate, db: Session = Depends(get_db)):
    task = Task(
        title=req.title,
        status=req.status,
        priority=req.priority,
        due_date=req.dueDate,
        project_id=req.projectId,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return _task_response(task)


@router.patch("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: str, req: TaskUpdate, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if req.title is not None:
        task.title = req.title
    if req.status is not None:
        task.status = req.status
    if req.priority is not None:
        task.priority = req.priority
    if req.dueDate is not None:
        task.due_date = req.dueDate
        
    db.commit()
    db.refresh(task)
    return _task_response(task)


@router.delete("/tasks/{task_id}")
def delete_task(task_id: str, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return {"status": "ok"}


@router.get("/{project_id}/assistant", response_model=ProjectAssistantResponse)
async def project_assistant(project_id: str, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    notes = db.scalars(select(Note).where(Note.project_id == project_id)).all()
    tasks = db.scalars(select(Task).where(Task.project_id == project_id)).all()
    pending = [task for task in tasks if task.status in {"todo", "in_progress"}]
    
    insights = await generate_project_insights(project, notes, pending)
    recent_notes = sorted(notes, key=lambda note: note.updated_at, reverse=True)[:5]

    return ProjectAssistantResponse(
        project=_project_response(project),
        noteCount=len(notes),
        taskCount=len(tasks),
        weeklySummary=insights["summary"],
        nextActions=insights["next_actions"],
        recommendedTags=insights["recommended_tags"],
        relatedNoteIds=[note.id for note in recent_notes],
    )


@router.post("/{project_id}/tasks/generate", response_model=GenerateTasksResponse)
async def generate_project_tasks(project_id: str, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    notes = db.scalars(select(Note).where(Note.project_id == project_id)).all()
    tasks = db.scalars(select(Task).where(Task.project_id == project_id)).all()
    pending = [task for task in tasks if task.status in {"todo", "in_progress"}]
    
    insights = await generate_project_insights(project, notes, pending)
    
    existing_titles = {t.title.lower() for t in tasks}
    created_tasks: list[Task] = []
    
    for title in insights["next_actions"]:
        if title.lower() in existing_titles:
            continue
        task = Task(
            title=title,
            status="todo",
            priority="medium",
            due_date=date.today() + timedelta(days=7),
            project_id=project_id,
        )
        db.add(task)
        created_tasks.append(task)

    db.commit()
    for task in created_tasks:
        db.refresh(task)

    return GenerateTasksResponse(
        created=len(created_tasks),
        tasks=[_task_response(task) for task in created_tasks],
    )


def _project_response(project: Project) -> ProjectResponse:
    return ProjectResponse(
        id=project.id,
        name=project.name,
        goal=project.goal,
        status=project.status,
        notionProjectPageId=project.notion_project_page_id,
        createdAt=project.created_at,
        updatedAt=project.updated_at,
    )


def _task_response(task: Task) -> TaskResponse:
    return TaskResponse(
        id=task.id,
        title=task.title,
        status=task.status,
        priority=task.priority,
        dueDate=task.due_date,
        projectId=task.project_id,
        sourceNoteId=task.source_note_id,
        createdAt=task.created_at,
        updatedAt=task.updated_at,
    )
