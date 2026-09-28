from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware, InterruptOnConfig
from langchain_core.messages import HumanMessage

from langchain_core.tools import tool

from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
import os
load_dotenv()

model = ChatOpenAI(
    model="kimi-k2.7-code",
    api_key=os.getenv("FZ_API_KEY"),
    base_url=os.getenv("FZ_BASE_URL")
)

@tool
def send_email(to:str,subject:str,body:str)->str:
    """send an email to a recipient
    Args:
        to(str):recipient to send to
        subject(str):subject of the email
        body(str):body of the email
        """
    return f"Email send to {to}：[{subject}]"

@tool
def read_user_profile(user_id:str)->str:
    """Read a user's profile information ,safe operation,no approval needed"""
    return f"Profile for {user_id}:Name=Alice,Role=Admin"

@tool
def delete_user(user_id: str)->str:
    """delete a user from the system
    Args:
        user_id(str):The user ID to delete
    """
    return f"user:{user_id} deleted"

agent = create_agent(
    model=model,
    tools=[send_email,read_user_profile,delete_user],
    system_prompt="你是一位ai助手",
    checkpointer=InMemorySaver(),
    middleware =[
        HumanInTheLoopMiddleware(
            description_prefix = "操作待审批",    # 自定义中断消息前缀
            interrupt_on={
                "send_email":InterruptOnConfig(allowed_decisions=["approve","edit","reject"]),
                "delete_user":InterruptOnConfig(allowed_decisions=["approve","reject"]), # 删除操作不允许编辑
                "read_user_profile":False,
            }
        )
    ]
)

config = {"configurable":{"thread_id":"hitl-session-001"}}
result = agent.invoke(
    {
        "messages":[
            HumanMessage(content="给john@example.com发一封会议通知邮件，主题是'项目评审会'"),
        ]
    },
    config = config,
    version="v2",  # 使用v2格式获取interrupts属性
)
if result.interrupts:
    interrupt_info = result.interrupts[0].value
    print("检测到中断，等待人工审批：")
    print(interrupt_info)
    # 输出示例:
    # {
    #   'action_requests': [{
    #       'name': 'send_email',
    #       'arguments': {
    #           'to': 'john@example.com',
    #           'subject': '项目评审会',
    #           'body': '...'
    #       },
    #       'description': '操作待审批：\n\nTool: send_email\nArgs: {...}'
    #   }],
    #   'review_configs': [{
    #       'action_name': 'send_email',
    #       'allowed_decisions': ['approve', 'edit', 'reject']
    #   }]
    # }


###人工审批
from langgraph.types import Command
result2 = agent.invoke(
    Command(
        resume={"decisions":[{"type":'approve'}]}
    ),
    config = config,
)

##人工编辑后批准

result2_edit= agent.invoke(
    Command(
        resume={
            "decisions":[{
                "type":'edit',
                "edited_action": {
                    'name':"send_email",
                    "args":{
                        "to":"john@company.com",
                        "subject": "【紧急】项目评审会通知",    # 修改主题
                       "body": "请准时参加明天下午2点的项目评审会。",
                    }},
            }]
        }
    ),config = config,
)
## 拒绝
result2_reject = agent.invoke(
    Command(
        resume={
            "decisions":[
                {
                    "tye":'reject',
                    "feedback":"该邮件需要经理审批，请先走内部审批流程",
                }
            ]
        }
    ),config = config,
)


###多工具并行

result_3 = agent.invoke(
    Command(
        resume={
            "decisions":[
                {"type": "approve"},
                {
                    "type": "edit",
                    "edited_action": {
                        "name": "delete_user",
                        "args": {"user_id": "user_789"}  # 修改删除目标
                    }
                }
            ]
        }
    ),config = config,
)


