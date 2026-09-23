####自定义agent工具
import datetime

from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv
load_dotenv()
import os

@tool
def get_work_date(date: str) -> str:
    """查看某一天是否有工作排班
    参数：date ->日期
    return : str
    """
    data={

    }
    return f'{date}有排班，需要工作'

@tool("today_date",description="获取今天的日期")
def get_time():
    """
    获取当前日期 的函数
    :return:
    """
    return datetime.datetime.now().strftime('%Y%m%d')

@tool(description="获取最近某一天的天气")
def get_weather(date:str)->str:
    """
    获取某一天的天气
    :param date: 日期
    :return:
    """
    return f"{date}会有大到暴雨，出行请备好雨伞,"

model = ChatOpenAI(
    model_name="kimi-k2.7-code",
    openai_api_key=os.getenv("FZ_API_KEY"),
    openai_api_base=os.getenv("FZ_BASE_URL")
)
agent = create_agent(
    model=model,
    tools=[get_work_date,get_time,get_weather],
    system_prompt="你是一位ai助手"
                     )
reply = agent.invoke({
    "messages":[("user","我明天需要上班吗,如果上的话需不需要带伞")]
})

print(reply["messages"][-1].content)
