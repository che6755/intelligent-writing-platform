from contextlib import asynccontextmanager
import os
import sys
from pathlib import Path
from sqlalchemy import select, text
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List 
import json
import re
import json_repair

from backend.app.db.session import Base, engine, get_db
from backend.app.schemas.document import DocumentCreate, DocumentUpdate, Document, ScoreReport
from backend.app.models.document import Document as DocumentModel
from backend.app.crud import crud_document
from backend.app.services.llm_service import llm_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        existing_columns = {
            row[1] for row in (await conn.execute(text("PRAGMA table_info(documents)"))).fetchall()
        }
        for column, definition in {
            "education_level": "VARCHAR NOT NULL DEFAULT 'high_school'",
            "language": "VARCHAR NOT NULL DEFAULT 'zh'",
            "title": "VARCHAR DEFAULT ''",
        }.items():
            if column not in existing_columns:
                await conn.execute(text(f"ALTER TABLE documents ADD COLUMN {column} {definition}"))
    yield

app = FastAPI(title="智能写作助手后端", lifespan=lifespan)

if getattr(sys, "frozen", False):
    frontend_dist = Path(sys._MEIPASS) / "frontend_dist"
else:
    frontend_dist = Path(__file__).resolve().parents[3] / "frontend" / "dist"

origins = [
    "http://localhost:5173",
    "http://localhost",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/generate-outline")
async def generate_outline(request: DocumentCreate):
    """
    生成写作大纲 (接入真实大模型)
    """
    prompt = f"请为主题 '{request.topic}' 生成一份详细的写作大纲。请以JSON格式返回，包含 'outline' (章节列表) 和 'materials' (素材列表) 两个字段。"

    return {
        "outline": [
            {"title": "引言", "content": "介绍背景，引出主题..."},
            {"title": "正文第一部分", "content": "详细阐述观点一..."},
            {"title": "正文第二部分", "content": "详细阐述观点二..."},
            {"title": "结论", "content": "总结全文，升华主题..."}
        ],
        "materials": [
            {"type": "名言", "content": "知识就是力量。"},
            {"type": "案例", "content": "某某名人的成功故事..."}
        ]
    }

@app.post("/api/ai-chat")
async def ai_chat(request: dict):
    """
    通用 AI 对话接口
    """
    user_message = request.get("message", "")
    if not user_message:
        raise HTTPException(status_code=400, detail="Message is required")

    response = await llm_service.generate_text(user_message)
    return {"reply": response}

@app.get("/api/documents", response_model=List[Document])
async def read_documents(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    # 按 ID 倒序排列，确保最新的文档在最前面
    result = await db.execute(select(DocumentModel).order_by(DocumentModel.id.desc()).offset(skip).limit(limit))
    return result.scalars().all()


@app.post("/api/documents", response_model=Document)
async def create_new_document(doc_in: DocumentCreate, db: AsyncSession = Depends(get_db)):
    """
    创建一个新的写作任务：
    1. 接收主题
    2. 调用 LLM 生成大纲
    3. 将主题和大纲存入数据库
    4. 返回创建好的文档对象，包含新的 ID
    """
    # 构造提示词
    education_label = "高中生" if doc_in.education_level == "high_school" else "大学生"
    language_label = "中文" if doc_in.language == "zh" else "英文"
    prompt = f"""
    用户身份：{education_label}
    作文语言：{language_label}
    作文类型：议论文
    输出语言：中文。除英文原文、英文改写句子和必要的英文专有名词外，标题、说明、原因、总结和建议都必须使用中文。
    请为主题 '{doc_in.topic}' 生成一份适合该用户身份和语言的详细议论文写作大纲。
    即使作文语言是英文，大纲标题和结构说明也请用中文，必要的英文例句可以保留英文。
    请严格按照以下 JSON 格式返回，不要包含任何其他文本或 Markdown 标记：
    {{
        "outline": [
            {{"title": "章节标题", "content": "章节内容简述"}}
        ],
        "materials": [
            {{"type": "素材类型(如名言/案例)", "content": "素材内容"}}
        ]
    }}
    """
    
    try:
        # 调用 LLM
        llm_response = await llm_service.generate_text(prompt, system_prompt="你是一个专业的写作助手。请只返回 JSON 格式的数据。")
        print(f"LLM 原始响应: {llm_response}") # 调试日志

        # 使用 json_repair 自动修复并解析 JSON
        outline_data = json_repair.loads(llm_response)
        
    except Exception as e:
        print(f"LLM 生成或解析失败: {e}")
        # 降级处理：如果生成失败，使用默认空结构，避免报错
        outline_data = {
            "outline": [{"title": "自动生成失败", "content": f"错误信息: {str(e)}"}],
            "materials": []
        }

    document = await crud_document.create_document(db=db, doc_in=doc_in, outline_data=outline_data)
    return document



@app.get("/api/documents/{doc_id}", response_model=Document)
async def read_document(doc_id: int, db: AsyncSession = Depends(get_db)):
    """
    根据 ID 获取一个写作任务的详细信息
    """
    db_doc = await crud_document.get_document(db=db, doc_id=doc_id)
    if db_doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return db_doc


@app.delete("/api/documents/{doc_id}", response_model=Document)
async def delete_document(doc_id: int, db: AsyncSession = Depends(get_db)):
    """
    删除一个写作任务
    """
    db_doc = await crud_document.delete_document(db=db, doc_id=doc_id)
    if db_doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return db_doc


# 其他 API (保存进度、提交评分) 将来会加在这里...


# 新增：保存写作进度的 API
@app.put("/api/documents/{doc_id}", response_model=Document)
async def save_document_progress(doc_id: int, doc_in: DocumentUpdate, db: AsyncSession = Depends(get_db)):
    db_doc = await crud_document.get_document(db=db, doc_id=doc_id)
    if not db_doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    updated_doc = await crud_document.update_document(db=db, db_obj=db_doc, obj_in=doc_in)
    return updated_doc

@app.post("/api/documents/{doc_id}/analysis")
async def analyze_document(doc_id: int, request: dict, db: AsyncSession = Depends(get_db)):
    db_doc = await crud_document.get_document(db=db, doc_id=doc_id)
    if not db_doc:
        raise HTTPException(status_code=404, detail="Document not found")

    action = request.get("action")
    allowed_actions = {
        "outline_hint", "example_hint", "grammar_check", "title_optimize",
        "logic_optimize", "style_polish", "example_expansion", "structure_check",
    }
    if action not in allowed_actions:
        raise HTTPException(status_code=400, detail="Unsupported analysis action")

    text = request.get("text") or db_doc.user_text or ""
    education_label = "高中生" if db_doc.education_level == "high_school" else "大学生"
    language_label = "中文" if db_doc.language == "zh" else "英文"
    action_instructions = {
        "outline_hint": "仅根据用户提供的作文主题，给出简洁的议论文结构提示，不要参考或改写正文。",
        "example_hint": "仅根据用户提供的作文主题，给出2到3个相关、可独立思考和查证的举例方向，不要参考正文，也不要直接代写段落。",
        "grammar_check": "找出全文中明确的语法、错别字或用词错误，返回所有错误。",
        "title_optimize": "检查用户提供的标题与正文是否匹配，评价标题是否切题、明确、简洁。若标题已经合适，必须明确返回‘标题无需修改’，不要为了提出建议而强行修改；只有确有必要时才给出最多3个替代标题。",
        "logic_optimize": "分析文章整体论证逻辑，只指出最重要的结构问题。",
        "style_polish": "只挑选最多3处最需要润色的句子，句式润色不是错误。",
        "example_expansion": "根据文章观点补充可使用的事实、案例或名言方向，避免编造具体事实。",
        "structure_check": "检查英文议论文的整体结构和论点展开，只指出最重要的问题。",
    }
    prompt = f"""
用户身份：{education_label}
作文语言：{language_label}
作文类型：议论文
    输出语言：中文。除原文、英文错误词和英文修改结果外，所有分析说明、错误原因、结构建议和总结都必须使用中文。
当前任务：{action_instructions[action]}
当前内容：
{text}

请只返回 JSON，不要使用 Markdown。返回结构：
{{"items":[{{"original":"原文或空字符串","suggestion":"建议","reason":"原因"}}],"summary":"总结"}}
标题优化时，当前内容是包含 title 和 body 的 JSON；必须同时参考标题与正文，但不要改写正文。
"""
    try:
        llm_response = await llm_service.generate_text(
            prompt,
            system_prompt="你是严格、克制的作文分析助手。只返回合法 JSON，并使用中文解释；英文内容只用于保留原句或给出修改后的英文句子。",
        )
        return json_repair.loads(llm_response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 分析服务出错: {str(e)}")

# 新增：提交评分的 API
@app.post("/api/documents/{doc_id}/score", response_model=ScoreReport)
async def score_document(doc_id: int, db: AsyncSession = Depends(get_db)):
    db_doc = await crud_document.get_document(db=db, doc_id=doc_id)
    if not db_doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if not db_doc.user_text or len(db_doc.user_text.strip()) < 10:
         raise HTTPException(status_code=400, detail="文章内容太少，无法评分")

    # 1. 调用 LLM 服务进行评分
    prompt = f"""
    用户身份：{"高中生" if db_doc.education_level == "high_school" else "大学生"}
    作文语言：{"中文" if db_doc.language == "zh" else "英文"}
    请对以下议论文进行评分和点评。
    请使用中文返回评分维度、点评和改进建议；英文作文中的原句和修改示例可以保留英文。
    标题：{db_doc.title or "（英文作文或未填写标题）"}
    文章内容：
    {db_doc.user_text}

    请严格按照以下 JSON 格式返回：
    {{
        "overall_score": 8.5,
        "dimensions": {{
            "内容切题": {{ "score": 9, "feedback": "点评..." }},
            "结构逻辑": {{ "score": 8, "feedback": "点评..." }},
            "语言表达": {{ "score": 8, "feedback": "点评..." }}
        }},
        "suggestions": [
            "改进建议1",
            "改进建议2"
        ]
    }}
    """
    
    try:
        llm_response = await llm_service.generate_text(prompt, system_prompt="你是一个专业的作文评分老师。请只返回 JSON 格式的数据。")
        print(f"评分 LLM 原始响应: {llm_response}") # 调试日志
        
        # 使用 json_repair 自动修复并解析 JSON
        score_data = json_repair.loads(llm_response)
        
    except Exception as e:
        print(f"评分失败: {e}")
        print(f"导致失败的响应内容: {llm_response if 'llm_response' in locals() else '未获取到响应'}")
        raise HTTPException(status_code=500, detail=f"AI 评分服务出错: {str(e)}")

    # 2. 将评分结果存入数据库
    await crud_document.update_score_report(db=db, db_obj=db_doc, score_data=score_data)

    # 3. 返回评分报告
    return score_data


if frontend_dist.is_dir():
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")