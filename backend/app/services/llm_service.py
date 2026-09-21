from openai import AsyncOpenAI
from backend.app.core.config import settings
import asyncio

class LLMService:
    def __init__(self):
        print(f"LLM Service Initialized with:")
        print(f"  Base URL: {settings.LLM_BASE_URL}")
        print(f"  Model: {settings.LLM_MODEL}")
        print(f"  API Key: {settings.LLM_API_KEY[:5]}...{settings.LLM_API_KEY[-5:] if settings.LLM_API_KEY else 'None'}")
        
        self.client = AsyncOpenAI(
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL,
            timeout=120.0,  # 增加超时时间到 120 秒
        )
        self.model = settings.LLM_MODEL

    async def generate_text(self, prompt: str, system_prompt: str = "You are a helpful writing assistant.", max_retries: int = 2) -> str:
        """
        调用大模型生成文本，带重试机制
        """
        last_error = None
        for attempt in range(max_retries + 1):
            try:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                )
                return response.choices[0].message.content
            except Exception as e:
                last_error = e
                print(f"LLM Error (attempt {attempt + 1}/{max_retries + 1}): {e}")
                if attempt < max_retries:
                    # 等待后重试（指数退避）
                    wait_time = (attempt + 1) * 2
                    print(f"等待 {wait_time} 秒后重试...")
                    await asyncio.sleep(wait_time)
        
        return f"生成失败: {str(last_error)}"

llm_service = LLMService() 
