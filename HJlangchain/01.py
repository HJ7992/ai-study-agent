from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()
import os


@tool()
def get_weather(city:str)->str:
    """
    查询某个城市的天气
    :param city: 城市名称
    :return:
    """
    weather_data={
        "北京": "晴天，25°C，微风",
        "上海": "多云，22°C，东南风3级",
        "深圳": "阵雨，28°C，湿度80%",
    }
    return weather_data.get(city,f"暂无{city}的天气数据")
@tool("nowtime",description="当需要获取当前时间时使用")
def get_time()->str:
    """获取当前时间"""
    from datetime import datetime
    return datetime.strftime(datetime.now(),"%Y-%m-%d %H:%M:%S")



model = ChatOpenAI(
    model='deepseek-flash',
    api_key=os.getenv("DS_API_KEY"),
    base_url=os.getenv("DS_URL"),
)

agent = create_agent(
    model=model,
    tools=[get_weather,get_time],
    system_prompt="你是一位ai助手"
)
# result = agent.invoke({"messages":[('user',"北京今天天气怎么样")]})
result = agent.invoke({"messages":[HumanMessage(content="现在几点了，深圳天气怎么样")]})
print(result['messages'][-1].content)
