from openai import AsyncOpenAI

from open_ai import config

client = AsyncOpenAI(
    api_key=config.OPEN_AI_API_KEY,
)
vityaz_model = [{
    "role": "system",
    "content": "Ты русский витязь. Ты участвовал во множестве битв за свою землю-матушку. Ты делишься своим опытом и знаниями с соратниками по службе. Поддерживай диалог и общайся как общался бы русский витязь."
}]


async def gpt_call(user_message: str) -> str:
    vityaz_model.append({"role": "user", "content": user_message})
    completion = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=vityaz_model,
        timeout=5
    )
    print(completion)
    content = completion.choices[0].message.content
    print(content)
    response = '' if content is None else str(content)
    vityaz_model.append({"role": "assistant", "content": response})

    return response
