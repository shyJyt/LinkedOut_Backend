from pathlib import Path

from openai import OpenAI

import sys

sys.path.append("..")

from config import MOONSHOT_API_KEY

client = OpenAI(
    api_key=MOONSHOT_API_KEY,
    base_url="https://api.moonshot.cn/v1",
)


def kimi(resume_path, resume_file_name):
    file_object = client.files.create(file=Path(resume_path), purpose="file-extract")

    # 获取结果
    # file_content = client.files.retrieve_content(file_id=file_object.id)
    # 注意，之前 retrieve_content api 在最新版本标记了 warning, 可以用下面这行代替
    # 如果是旧版本，可以用 retrieve_content
    file_content = client.files.content(file_id=file_object.id).text

    # 把它放进请求中
    messages = [
        {
            "role": "system",
            "content": "你是 Kimi，由 Moonshot AI 提供的人工智能助手，你更擅长中文和英文的对话。你会为用户提供安全，有帮助，准确的回答。同时，你会拒绝一切涉及恐怖主义，种族歧视，黄色暴力等问题的回答。Moonshot AI 为专有名词，不可翻译成其他语言。",
        },
        {
            "role": "system",
            "content": file_content,
        },
        {
            "role": "user",
            "content": resume_file_name + "是一份待优化的简历，请给出优化建议。",
        },
    ]

    # 然后调用 chat-completion, 获取 Kimi 的回答
    response = client.chat.completions.create(
        model="moonshot-v1-32k", messages=messages, temperature=0.3, stream=True
    )

    for _, chunk in enumerate(response):
        chunk_message = chunk.choices[0].delta
        if not chunk_message.content:
            continue
        yield chunk_message.content
