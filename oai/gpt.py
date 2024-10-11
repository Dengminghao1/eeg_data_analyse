
from openai import OpenAI
client = OpenAI(api_key="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")

completion = client.chat.completions.create(
  model="gpt-4o-mini",

  messages=[
    {"role": "system", "content": "你是情绪分析专家"},
    {"role": "user", "content": "你是谁"}
  ]
)

print(completion.choices[0].message.content)
