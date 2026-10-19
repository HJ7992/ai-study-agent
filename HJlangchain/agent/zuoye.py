import json
import os
from dotenv import load_dotenv
load_dotenv()
from openai import OpenAI
client = OpenAI(
    base_url=os.getenv("FZ_BASE_URL"),
    api_key=os.getenv("FZ_API_KEY"),
)
tools = [
    {
        "type":"function",
        "function":{
            "name" :"get_current_weather",
            "description" :"查询某地的天气情况",
            "parameters" : {
                "type" : "object",
                "properties" : {
                    "city" :{
                        "type" : "string",
                        "description" : "城市，列如北京",
                    },
                    "units" :{
                        "type" : "string",
                        "enum" :  ["metric", "imperial"],
                        "description" : "使用的温度单位",
                        "default" : "metric",
                    }
                }
            },
            "required":["city"],
        }
    }
]

import requests
def get_current_weather(city : str,units : str = 'metric') :
    api_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=5&appid={os.getenv("WEATHER_API_K")}"
    response = requests.get(api_url)
    data = response.json()
    if response.status_code == 200:
        lat = data[0]["lat"]
        lon = data[0]["lon"]
        base_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={os.getenv("WEATHER_API_K")}"
        response = requests.get(base_url)
        data_weather = response.json()
        if response.status_code == 200:
            weather = {
                'temperature': data_weather['main']['temp'],
                'description': data_weather['weather'][0]['description'],
                'city': data_weather['name'],
                'country': data_weather['sys']['country']
            }
            return weather
        else:
            return {"error": data.get("message", "An error occurred.")}
    else:
        return {"error": data.get("message", "An error occurred.")}

messages = []
messages.append({"role":"system","content":"不要假设或猜测传入函数的参数值，如果用户的描述不明确，请要求用户提供必要信息"})

messages.append({"role":"user","content":f"帮我查一下北京的天气"})
response = client.chat.completions.create(
    model='deepseek-v4-flash',
    messages=messages,
    temperature=0.6,
    tools=tools,
)

if response.choices[0].message.tool_calls:
    tool_call = response.choices[0].message.tool_calls[0]
    args = tool_call.function.arguments
    function_result = {}
    if tool_call.function.name == "get_current_weather":
        function_result = get_current_weather(**json.loads(args))
    messages.append({"role":"tool","content":f"{json.dumps(function_result)}","tool_call_id" :tool_call.id})
    response = client.chat.completions.create(
        model='deepseek-v4-flash',
        messages=messages,
        temperature=0.6,
        tools=tools,
    )
    print(response.choices[0].message.content)

