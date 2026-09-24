# 智能写作平台

一个面向高中生和大学生的 AI 议论文写作辅助平台。项目采用前后端分离架构，帮助用户从确定主题开始，完成大纲生成、在线写作、针对性分析和 AI 评分。

## 项目亮点

- **分阶段写作流程**：主题创建、大纲准备、正文编辑、分析优化、提交评分形成完整闭环。
- **适配不同写作者**：支持高中和大学两种写作者身份，并支持中文、英文议论文模式。
- **AI 写作辅助**：提供大纲提示、举例提示、语法检查、标题优化、逻辑优化、句式润色和结构检查等能力。
- **富文本编辑体验**：集成本地 TinyMCE，支持常用文本格式、列表、链接、表格、字数统计和自动保存。
- **评分报告留存**：从内容切题、结构逻辑、语言表达等维度生成评分和改进建议，并保存到历史记录。
- **本地化运行**：默认使用 SQLite 保存数据，前端内置 TinyMCE 静态资源，适合本地开发、演示和容器化部署。

## 功能流程

```text
选择写作者身份和作文语言
          |
       输入主题
          |
   AI 生成写作大纲与素材
          |
      进入在线编辑器
       /          \
自动保存正文       获取写作辅助
       |       （纠错、结构、举例等）
       \          /
       提交全文进行 AI 评分
          |
   查看评分报告与改进建议
```

## 页面说明

### 首页

- 查看历史写作任务。
- 区分草稿和已评分文章。
- 继续写作或删除历史记录。
- 选择高中或大学写作者身份。

### 新建创作

- 选择写作者身份：高中或大学。
- 选择作文语言：中文议论文或英文议论文。
- 输入作文主题并创建写作任务。
- 创建时由后端调用大模型准备基础大纲和素材。

### 在线编辑器

- 中文作文支持输入文章标题。
- 使用 TinyMCE 编辑正文。
- 自动保存写作进度。
- 可按需获取大纲提示、举例提示或语法检查。
- 完成写作后提交全文，生成 AI 评分报告。

### 评分与分析

评分完成后，编辑器会展示：

- 总分及满分比例。
- 各评分维度的分数和点评。
- 针对文章内容的改进建议。
- 标题优化、语法检查、逻辑优化、样例扩充、句式润色等后续分析操作。

## 技术架构

```text
Vue 3 + Vite + TinyMCE
          |
      Axios
          |
FastAPI + SQLAlchemy Async
          |
       SQLite 数据库
          |
 OpenAI 兼容接口 / 大模型服务
```

### 前端

- Vue 3
- Vite
- Vue Router
- Axios
- TinyMCE 8

前端源码位于 [`frontend/src`](frontend/src)，主要页面位于 [`frontend/src/views`](frontend/src/views)。

### 后端

- FastAPI
- Uvicorn
- SQLAlchemy Async
- aiosqlite
- Pydantic Settings
- OpenAI SDK
- json-repair

后端入口位于 [`backend/app/main.py`](backend/app/main.py)，模型服务封装位于 [`backend/app/services/llm_service.py`](backend/app/services/llm_service.py)。

### 数据存储

默认使用 SQLite，数据库文件会根据运行模式放在项目数据目录中。文档数据主要包括：

- 作文主题、标题和正文。
- 写作者身份和作文语言。
- AI 生成的大纲与素材。
- 创建时间和更新时间。
- AI 评分报告。

## 快速开始

### 方式一：本地开发

#### 1. 准备后端环境

建议使用 Python 3.10 或更高版本：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
```

#### 2. 配置大模型服务

复制 `.env.example` 为项目根目录下的 `.env`，并填写兼容 OpenAI 接口的大模型服务配置：

```dotenv
LLM_API_KEY=你的API密钥
LLM_BASE_URL=模型服务接口地址
LLM_MODEL=模型名称
```

也可以在 [`backend/.env`](backend/.env) 中配置。请勿将包含真实密钥的 `.env` 提交到版本库。

#### 3. 启动后端

在项目根目录执行：

```powershell
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

后端接口文档地址：<http://127.0.0.1:8000/docs>

#### 4. 启动前端

```powershell
cd frontend
npm install
npm run dev
```

浏览器打开 <http://localhost:5173>。

### 方式二：Docker Compose

在项目根目录准备 `.env`，然后执行：

```powershell
docker compose up --build
```

默认访问地址为 <http://localhost:8080>。也可以通过 `APP_PORT` 修改宿主机端口：

```dotenv
APP_PORT=8080
LLM_API_KEY=你的API密钥
LLM_BASE_URL=模型服务接口地址
LLM_MODEL=模型名称
```

## 主要接口

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| `GET` | `/api/documents` | 获取历史文档列表 |
| `POST` | `/api/documents` | 创建文档并生成初始大纲 |
| `GET` | `/api/documents/{id}` | 获取文档详情 |
| `PUT` | `/api/documents/{id}` | 保存写作进度 |
| `DELETE` | `/api/documents/{id}` | 删除文档 |
| `POST` | `/api/documents/{id}/analysis` | 执行指定的 AI 分析任务 |
| `POST` | `/api/documents/{id}/score` | 提交文章并生成评分报告 |

## 目录结构

```text
intelligent-writing-platform/
├── backend/
│   └── app/
│       ├── main.py                 # FastAPI 应用入口和接口
│       ├── core/config.py          # 环境变量和路径配置
│       ├── crud/                   # 文档数据操作
│       ├── db/                     # 异步数据库会话
│       ├── models/                 # SQLAlchemy 数据模型
│       ├── schemas/                # Pydantic 请求与响应模型
│       └── services/llm_service.py # 大模型服务封装
├── frontend/
│   ├── src/
│   │   ├── views/                  # 首页、创建页、编辑器、使用说明
│   │   ├── router/                 # 前端路由
│   │   └── config.js               # API 地址配置
│   └── public/tinymce/             # 本地 TinyMCE 资源
├── docker-compose.yml
├── .env.example
└── README.md
```

## 开发说明

- 前端默认通过 `/api` 访问后端；开发环境下的代理配置见 [`frontend/vite.config.js`](frontend/vite.config.js)。
- 后端会在启动时创建或补充 SQLite 数据表结构。
- 大模型返回内容使用 `json-repair` 尝试修复后再解析，降低格式不规范导致的失败。
- `/api/generate-outline` 当前保留了一份用于演示的固定大纲响应；实际创建文档流程使用 `/api/documents`。
- 未配置大模型服务时，创建、分析和评分相关功能无法正常调用真实 AI 能力，但前端和基础文档管理功能仍可用于调试。

## 构建前端

```powershell
cd frontend
npm run build
npm run preview
```

构建产物位于 `frontend/dist`。后端在检测到该目录后，可以在部署模式下托管前端静态文件。

## 项目定位

本项目适合作为以下场景的基础实现：

- AI 辅助作文与议论文写作工具。
- 大模型调用、结构化 JSON 输出和结果修复的实践项目。
- Vue 3、FastAPI 和异步数据库的全栈示例。
- 可继续扩展用户系统、文章导出、更多作文类型和个性化评分标准的写作平台。
