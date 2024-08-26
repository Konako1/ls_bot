import configparser
import random
from typing import Optional

from openai import AsyncOpenAI

from open_ai.config import Config

client = AsyncOpenAI(
    api_key=Config.read('OPEN_AI_API_KEY'),
)


async def gpt_call(user_message: str, model: list[dict[str, str]]) -> Optional[str]:
    model.append({"role": "user", "content": user_message})
    rand = random.randrange(0, Config.read('CALL_PROBABILITY'))
    if rand != 0:
        return None
    completion = await client.chat.completions.create(
        model="gpt-4",
        messages=model,
        timeout=5,
        temperature=1,
        top_p=1
    )
    content = completion.choices[0].message.content
    usage = completion.usage
    tokens = f"Completion: {usage.completion_tokens}. Prompt: {usage.prompt_tokens}. Total: {usage.total_tokens}. {completion.model}"
    response = '' if content is None else str(content)
    model.append({"role": "assistant", "content": response})

    return f"{response}\n\n{tokens}"
