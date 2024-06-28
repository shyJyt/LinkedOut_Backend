from openai import OpenAI

import sys

sys.path.append('..')

from config import MOONSHOT_API_KEY
 
client = OpenAI(
    api_key = MOONSHOT_API_KEY,
    base_url = "https://api.moonshot.cn/v1",
)