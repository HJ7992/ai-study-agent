##3、开发一个可以查航班的里程价格的程序。
# 第一步需要查出发地和目的地的航班号（需要参数出发地和目的地和日期），
##第二步需要根据航班号查价格(航班号和舱位)
from typing import Any

import requests
tools = [
    {
        "type" : "function",
        "function":{
            "name" : "get_flight_number",
            "description":"查询指定日期出发地到目的地的航班信息",
            "parameters":{
                "type":"object",
                "properties":{
                    "departure":{
                        "type":"string",
                        "description":"出发地城市或机场的IATA代码，输入名称则无效"
                    },
                    "destination":{
                        "type":"string",
                        "description":"目的地城市或机场的IATA代码，输入名称则无效"
                    },
                    "date":{
                        "type":"string",
                        "description":"日期，如：2025-12-21"
                    }
                }
            },
            "required":["departure","destination","date"]
        }
    }
]

def get_flight_number(departure : str,destination : str,date : str) -> Any:
    """
    description : 某个日期出发地到目的地的航班号
    Parameters :
     departure : str 出发地城市或机场（IATA代码）
     destination : str 目的地城市或机场（IATA代码）
     date : str 日期如：2025-12-21
    """
    if not destination or not departure or not date:
        print("参数有误")
        return
    api_url = "https://apis.juhe.cn/flight/query"
    api_key = "50dd9b45d56767c7ed7f71a7197c11d1"

    request_params = {
        'key': api_key,
        'departure': departure,
        'arrival': destination,
        'departureDate': date,
        'flightNo': '',
        'maxSegments': '',
    }
    try:
        response = requests.get(api_url, params=request_params)
    except requests.exceptions.RequestException as e:
        print(f"错误信息{e}")
        return "请求获取错误"
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return "未获取到航班数据"

if __name__ == "__main__":
    import json
    import os
    from dotenv import load_dotenv

    load_dotenv()
    from openai import OpenAI

    client = OpenAI(
        base_url=os.getenv("FZ_BASE_URL"),
        api_key=os.getenv("FZ_API_KEY"),
    )
    messages = []
    messages.append({"role":"system","content":"你是个人助手张三，目前可以帮助用户查询航班信息，你的数据必须真实有效，禁止胡编乱造"})
    messages.append({"role":"user","content":"帮我查一下26年10月14日从深圳到昆明的航班"})
    response = client.chat.completions.create(
        model='deepseek-v4-flash',
        messages=messages,
        temperature=0.6,
        tools=tools,
    )
    messages.append(response.choices[0].message.model_dump())
    print("发起调用工具请求")
    if response.choices[0].message.tool_calls[0]:
        tool_call = response.choices[0].message.tool_calls[0]
        args = tool_call.function.arguments
        tool_result = {}
        if tool_call.function.name == "get_flight_number":
            tool_result = get_flight_number(**json.loads(args))
        messages.append({"role":"tool","content":json.dumps(tool_result)})
        response = client.chat.completions.create(
            model='deepseek-v4-flash',
            messages=messages,
            temperature=0.6,
            tools=tools,
        )
        print(response.choices[0].message.content)
    else:
        print(response.choices[0].message.content)

