import os
from dotenv import load_dotenv
from huggingface_hub.utils import endpoint_helpers

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
load_dotenv()
"""创键客户端链接"""
model = ChatOpenAI(
    model_name="kimi-k2.7-code",
    openai_api_key=os.getenv("FZ_API_KEY"),
    openai_api_base=os.getenv("FZ_BASE_URL")
)

checkpointer = InMemorySaver()

agent = create_agent(
    model=model,
    tools=[],
    system_prompt="你是助手",
    checkpointer=checkpointer,
)
user_text = """我叫王大锤，万万没想到，我居然穿越了，
                       这是一个修仙世界。我在这里生活了1000多年，
                       终于修行到了练气二期，明天我要去靠山宗和王二麻对战，
                       只要这次赢了，我就能得到小美 的芳心了，嘿嘿嘿
                       """
config = {"configurable": {"thread_id": "session-001"}}

reply = agent.invoke({
    "messages":[("user",user_text)]
},config=config)
print(f"R:{user_text}")
print(f"AI: {reply['messages'][-1].content}")
text2= "今天是第二天了，我应该做啥来着？"
reply2 = agent.invoke({
    "messages":[("user",text2)]
},config=config)
print(f"R:{text2}")
print(f"AI: {reply2['messages'][-1].content}")

while True:
    message = input("U:",)
    if message:
        reply = agent.invoke({
            "messages": [("user", message)]
        }, config=config)
        print(f"AI: {reply['messages'][-1].content}")
    else:
        break

