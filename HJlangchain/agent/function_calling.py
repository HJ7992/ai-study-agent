import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url=os.getenv("FZ_BASE_URL"),
    api_key=os.getenv("FZ_API_KEY"),
)
tools = [
    {
        "type": "function",
        "function":{
            "name" : "get_flight_number",
            "description":"",
            "parameters":{
                "type":"object",
                "properties":{
                    "departure":{
                        "type":"string",
                        "description":"出发地",
                    },
                    "destination":{
                        "type":"string",
                        "description":"目的地"
                    },
                    "date":{
                        "type":"string",
                        "description":"日期"
                    }
                }
            },
            "required":["departure","destination","date"]
        }
    },
    {
        "type": "function",
        "function":{
            "name" : "get_ticket_price",
            "description":"查询某航班在某日的票价",
            "parameters":{
                "type":"object",
                "properties":{
                    "flight_number":{
                        "type":"string",
                        "description" :"航班号"
                    },
                    "date":{
                        "type":"string",
                        "description":"日期"
                    }
                }
            },
            "required":["flight_number","date"]
        }
    }
]

#自定义函数
def get_flight_number(departure : str,destination : str,date : str):
    flight_number = {
        "北京":{
            "上海" : "1234",
            "广州" : "8321"
        },
        "上海" : {
            "北京" : "2344",
            "广州" : "3455",
        }
    }
    return {"flight_number" : flight_number[departure][destination]}

def get_ticket_price(flight_number : str,date : str):
    return {"ticket_price" : "1000"}




##print(response.choices[0].message)

def parse_function_call(model_response,messages):
    if model_response.tool_calls:
        tool_call = model_response.tool_calls[0]
        args = tool_call.function.arguments
        function_result = {}
        if tool_call.function.name == "get_flight_number":
            function_result = get_flight_number(**json.loads(args))
        if tool_call.function.name == "get_ticket_price":
            function_result = get_ticket_price(**json.loads(args))
        messages.append({
            "role":"tool",
            "content":f"{json.dumps(function_result)}",
            "tool_call_id":tool_call.id,
        })
        response = client.chat.completions.create(
            model='deepseek-v4-flash',
            messages=messages,
            temperature=0.6,
            tools=tools,
        )
        print(response.choices[0].message.content)
        messages.append(response.choices[0].message.model_dump())
    return messages



messages = []
messages.append({"role":"system","content":"不要假设或猜测传入函数的参数值，如果用户的描述不明确，请要求用户提供必要信息"})
messages.append({"role":"user","content":"帮我查询从24年1月20号开始，从北京出发前往上海 的航班"})
response = client.chat.completions.create(
    model='deepseek-v4-flash',
    messages=messages,
    temperature=0.6,
    tools=tools,
)
print(f"请求调用工具的内容 ：{response.choices[0].message}")
messages.append(response.choices[0].message.model_dump())
re_messages = parse_function_call(model_response=response.choices[0].message,messages=messages)
messages = re_messages

messages.append({"role":"user","content":"帮我查一下价格是多少"})
response = client.chat.completions.create(
    model='deepseek-v4-flash',
    messages=messages,
    temperature=0.6,
    tools=tools,
)
print(f"请求调用工具的内容 ：{response.choices[0].message}")
messages.append(response.choices[0].message.model_dump())
parse_function_call(model_response=response.choices[0].message,messages=messages)
