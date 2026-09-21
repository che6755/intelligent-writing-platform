from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.app.models.document import Document
from backend.app.schemas.document import DocumentCreate, DocumentUpdate


# 定义一个辅助函数，用于深度清理数据中的 Ellipsis 值
# 它可以递归地处理嵌套的字典和列表
async def update_document(db: AsyncSession, *, db_obj: Document, obj_in: DocumentUpdate) -> Document:
    """
    更新文档的文本内容
    """
    db_obj.user_text = obj_in.user_text
    if obj_in.title is not None:
        db_obj.title = obj_in.title
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def update_score_report(db: AsyncSession, *, db_obj: Document, score_data: dict) -> Document:
    """
    更新文档的评分报告
    """
    db_obj.score_report = score_data
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

def clean_ellipsis(data: Any) -> Any:
    """
    Recursively remove Ellipsis values from dictionaries and lists.
    """
    if isinstance(data, dict):
        # 如果是字典，为每个键值对递归调用本函数，并只保留值不是 ... 的项
        cleaned_dict = {}
        for k, v in data.items():
            if v is not ...:
                cleaned_dict[k] = clean_ellipsis(v)
        return cleaned_dict
    elif isinstance(data, list):
        # 如果是列表，为每个元素递归调用本函数，并只保留不是 ... 的项
        return [clean_ellipsis(item) for item in data if item is not ...]
    else:
        # 如果是其他数据类型（字符串、数字等），直接返回
        return data


async def create_document(db: AsyncSession, *, doc_in: DocumentCreate, outline_data: dict) -> Document:
    # 1. 在使用 outline_data 之前，先调用辅助函数进行清洗
    cleaned_outline_data = clean_ellipsis(outline_data)
    
    # 2. 使用清洗过后的 cleaned_outline_data 来创建数据库对象
    db_obj = Document(
        topic=doc_in.topic,
        education_level=doc_in.education_level,
        language=doc_in.language,
        title=doc_in.title,
        outline=cleaned_outline_data,
    )
    
    # 后面的逻辑保持不变
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def get_document(db: AsyncSession, doc_id: int) -> Document | None:
    result = await db.execute(select(Document).filter(Document.id == doc_id))
    return result.scalars().first()


async def delete_document(db: AsyncSession, doc_id: int) -> Document | None:
    result = await db.execute(select(Document).filter(Document.id == doc_id))
    db_obj = result.scalars().first()
    if db_obj:
        await db.delete(db_obj)
        await db.commit()
    return db_obj