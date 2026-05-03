# MindDock

MindDock 是一个本地优先的个人知识库和项目工作台。它用于收集笔记、用 AI 自动分类和总结、关联项目、生成任务，并基于本地知识库进行带引用的问答。

当前版本是一个 Vue 3 + FastAPI 原型，已经具备可运行的本地前后端、Notion 集成入口、项目/任务管理、本地与 AI 复盘流程，以及初步的 RAG 问答能力。

## 当前完成情况

| 模块 | 状态 | 说明 |
| --- | --- | --- |
| Web 应用框架 | 已完成 | Vue 3、Vite、Pinia、Vue Router、Naive UI；包含收集箱、知识问答、项目、复盘、设置页面。 |
| 笔记收集 | 已完成 | 可在收集箱中新建笔记，自动分类、摘要、打标签，并保存到本地数据库。 |
| Notion 同步 | 部分完成 | 配置凭证后，可将新笔记写入 Notion，也可从 Notion 数据库导入页面；暂未实现 OAuth。 |
| 项目管理 | 已完成 | 支持创建、查看、删除项目，并将笔记关联到项目。 |
| 任务管理 | 已完成 | 支持创建、更新、完成、删除任务，也可基于项目上下文自动生成任务。 |
| 知识问答 | 部分完成 | 配置 OpenAI 后使用 embedding/RAG；未配置时回退到本地关键词检索。 |
| 复盘 | 部分完成 | 支持本地每日/每周统计；AI 每周复盘需要配置 `OPENAI_API_KEY`。 |
| 设置 | 部分完成 | 支持保存单用户开发环境下的 Notion 与模型偏好；生产级认证和多用户隔离尚未完成。 |
| Supabase | 已脚手架化 | `supabase/migrations` 下有初始 schema，但当前运行时主要通过 SQLAlchemy 和 `DATABASE_URL` 连接数据库。 |

## 主要功能

- 在收集箱中快速保存笔记到本地数据库。
- 自动生成笔记标题、摘要、类型、标签和行动项。
- 可选将捕获的笔记同步创建到 Notion。
- 从配置好的 Notion 数据库同步页面到本地。
- 管理项目和项目下的任务。
- 根据项目笔记生成项目洞察、下一步建议、推荐标签和任务。
- 基于本地笔记进行知识问答，并返回引用来源。
- 生成每日复盘和每周复盘。
- 在设置页配置 Notion 和 AI 模型偏好。

## 技术栈

- 前端：Vue 3、Vite、TypeScript、Pinia、Vue Router、Naive UI、Axios。
- 后端：FastAPI、SQLAlchemy 2、Pydantic Settings、Uvicorn。
- AI：OpenAI Chat 和 Embeddings；预留 Anthropic、Gemini、DeepSeek 配置。
- 集成：Notion API、Supabase migration 脚手架。
- 数据库：默认使用 MySQL；也可通过 SQLAlchemy 连接 PostgreSQL 或 SQLite。

## 目录结构

```text
.
├── backend/                 # FastAPI 应用、模型、服务、API 路由
├── frontend/                # Vue 3 前端应用
├── supabase/migrations/     # Supabase/Postgres 初始 schema 草稿
├── start.sh                 # 本地启动、停止、查看状态脚本
├── .env.example             # 根目录环境变量示例
└── README.md
```

## 环境要求

- Node.js 和 npm
- Python 3.11+
- 一个与 `DATABASE_URL` 匹配的可用数据库
- 可选：OpenAI API Key，用于 embeddings、RAG 回答、AI 分类和 AI 复盘
- 可选：Notion integration token 和数据库 ID，用于 Notion 同步

## 环境变量

复制环境变量示例：

```bash
cp .env.example .env
```

常用配置：

```bash
DATABASE_URL=mysql+pymysql://root@localhost:3306/minddock
OPENAI_API_KEY=your-openai-key
NOTION_INTEGRATION_TOKEN=your-notion-token
NOTION_NOTES_DATABASE_ID=your-notion-notes-database-id
DEEPSEEK_API_BASE=https://api.deepseek.com/v1
DEEPSEEK_API_KEY=your-deepseek-key
DEEPSEEK_MODEL_NAME=deepseek-chat
```

如果没有设置 `DATABASE_URL`，后端默认使用：

```bash
mysql+pymysql://root@localhost:3306/minddock
```

如果只是快速本地试用，也可以使用 SQLite：

```bash
DATABASE_URL=sqlite:///./minddock.db
```

## 本地运行

在仓库根目录执行：

```bash
./start.sh
```

脚本会安装缺失的前端依赖，创建 `backend/.venv`，安装后端依赖，并启动前后端服务：

- 前端：http://localhost:5173
- 后端：http://localhost:8000
- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/api/health

查看状态或停止服务：

```bash
./start.sh status
./start.sh stop
```

## 手动开发

后端：

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

前端：

```bash
cd frontend
npm install
npm run dev
```

构建前端：

```bash
cd frontend
npm run build
```

## API 概览

后端 API 统一挂载在 `/api/v1` 下。

- `GET /api/health`：服务健康检查。
- `GET /api/v1/notes`：获取笔记列表。
- `POST /api/v1/notes/capture`：捕获并分类一条笔记。
- `POST /api/v1/notes/sync/notion`：从 Notion 导入笔记。
- `PATCH /api/v1/notes/{note_id}`：更新笔记。
- `DELETE /api/v1/notes/{note_id}`：删除笔记。
- `GET /api/v1/projects`：获取项目和任务列表。
- `POST /api/v1/projects`：创建项目。
- `GET /api/v1/projects/{project_id}/assistant`：生成项目洞察。
- `POST /api/v1/projects/{project_id}/tasks/generate`：根据项目上下文生成任务。
- `POST /api/v1/projects/tasks`：创建任务。
- `PATCH /api/v1/projects/tasks/{task_id}`：更新任务。
- `POST /api/v1/chat/ask`：基于笔记进行知识问答。
- `GET /api/v1/review/weekly`：生成 AI 每周复盘。
- `GET /api/v1/settings` / `PATCH /api/v1/settings`：读取或更新开发用户设置。

## 数据与安全说明

- 不要提交 `.env`、本地数据库文件、日志或进程文件。
- `service_role` 和其他密钥只能放在服务端，不能暴露到前端。
- 设置页目前是单用户开发流程，不是生产级认证系统。
- Notion 凭证可以通过应用保存，但暂未实现 OAuth、令牌轮换和完整权限管理。
- 如果后续将 Supabase schema 暴露到公开 API，需要先审查并完善 RLS 策略。

## 已知缺口

- 暂无生产级认证和多用户隔离。
- Supabase schema 已存在，但当前后端运行仍主要依赖 SQLAlchemy 和 `DATABASE_URL`。
- 未配置 API Key 时，AI 功能会降级；完整 RAG 回答和 AI 每周复盘需要 OpenAI 配置。
- 还没有提交自动化测试套件。
- 尚未加入部署配置。
