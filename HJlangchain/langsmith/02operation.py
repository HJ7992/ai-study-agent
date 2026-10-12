# 第1步：设置 API Key
# 去 https://smith.langchain.com/settings 注册并获取你的 Key
import os

# 从 .env 或环境变量读取，避免将 Key 硬编码到代码里
from dotenv import load_dotenv

load_dotenv()
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY", "")

# 第2步：开启追踪开关
# 设为 "true" 表示开始记录；设为 "false" 可以随时关闭
os.environ["LANGSMITH_TRACING"] = "true"

# 第3步：指定项目名称
# 同一个项目的所有 Trace 会自动归到一起，方便管理
os.environ["LANGSMITH_PROJECT"] = "langsmith"

from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langsmith import traceable

@traceable(run_type="llm",metadata={"model":"deepseek"},tags=["langsmith"])
def translate_text(text : str, target_lang : str) ->str:
    prompt = PromptTemplate.from_template(
        """
        你是一位翻译助手，请将下面的文本内容转换为指定的语言.
        文本：{text}\n
        目标语言{target_lang}
        禁止输出无关内容。
        """
    )
    llm = ChatOpenAI(model="deepseek-v4.1-flash",base_url="https://ark.cn-beijing.volces.com/api/coding/v3")
    chain = prompt | llm
    response = chain.invoke(input={"text":text,"target_lang":target_lang}).content
    return response

@traceable(run_type="llm",datameta={"model":"openai"},tags=["langsmith"])
def summary_text(text : str) ->str:
    prompt = ChatPromptTemplate.from_messages([
        ("system","你是一位内容摘要助手，负责将传入的对话文本提取为摘要"),
        ("human","以下为消息内容，请提取摘要：{text}")
    ])
    llm = ChatOpenAI(model="deepseek-v4.1-flash",base_url="https://ark.cn-beijing.volces.com/api/coding/v3")
    chain = prompt | llm
    response = chain.invoke(input={"text":text}).content
    return response


@traceable(run_type="llm",metadata={"userId":"Hj7992"},tags=["translation-pipeline"])
def translate_and_summary(example : dict[str,str]) ->str:
    """对内容进行摘要并翻译为英文"""
    summary = summary_text(example['text'])
    return translate_text(summary, example['target_lang'])

if __name__ == "__main__":
    text = "LangSmith 是 LangChain 推出的 LLM 应用开发与运维平台，用于追踪、调试、测试、评估和监控大语言模型应用及智能体。"
    target_lang = "English"
    #print(translate_text(text, target_lang))
    #print("翻译完成========================================================")
    #print("摘要测试开始=====================================================")
    summary_text_1 = """
    hunman:'我的理想是当太空人，你有什么建议吗？
    ai : 
    有这样一个理想真的很棒！太空人（航天员）确实是很多人心中的英雄，但这个职业也确实需要极其苛刻的条件和长期的努力。给你一些具体建议，希望能帮你把这份理想一步步落地。

**1. 先搞清楚“太空人”到底有哪些类型**
航天员不只有一种，不同方向要求差别很大：
- **飞行员航天员**：通常从空军飞行员中选拔，对飞行时长、身体素质要求极高。
- **任务专家/载荷专家**：更偏向科研背景，比如物理、生物、医学、工程等博士，负责空间实验。
- **商业航天员**：随着商业航天发展，未来可能更多，但门槛和费用目前仍很高。

你可以先了解中国航天员科研训练中心、NASA、SpaceX等机构的选拔标准，看看自己更接近哪条路。

**2. 身体是硬门槛，现在就要保护**
- 视力：很多航天选拔对近视有严格限制，尽量别让视力恶化。
- 身高体重：航天员通常有身高范围要求（比如中国航天员一般在1.6-1.75米左右），保持匀称体型。
- 前庭功能：多做一些平衡训练，比如旋转、荡秋千，但别过度。
- 心肺功能：坚持长跑、游泳等有氧运动。
- 别碰烟酒、熬夜，这些都会影响长期健康。

**3. 学业方向要选对**
- 如果走飞行员路线：高中阶段就要关注空军招飞，通常要求理科好、身体素质过硬。
- 如果走科研路线：大学选**航空航天、力学、物理、生物医学工程、材料、计算机**等专业，争取读到博士。
- 英语非常重要，国际合作和文献阅读都离不开。
- 可以关注**北京航空航天大学、哈尔滨工业大学、国防科技大学、清华大学**等有航天相关专业的学校。

**4. 积累“太空相关”的经历**
- 参加航天模型、火箭设计、卫星编程等竞赛。
- 关注并尝试申请**航天夏令营、空间站载荷实验征集**等活动。
- 如果条件允许，考取**私用驾驶员执照（PPL）**，积累飞行经验。
- 学习潜水、跳伞、野外生存，这些和航天训练有相通之处。

**5. 心理素质也要练**
航天员要能在密闭、孤独、高压环境下保持冷静。平时可以：
- 多参加团队协作和领导力活动。
- 练习冥想、正念，提高情绪调节能力。
- 遇到挫折时，学会把它当成训练的一部分。

**6. 现实一点：做好备选路径**
航天员选拔极其残酷，可能你最后没成为航天员，但沿着这条路走，你可能会成为：
- 飞行员、工程师、科学家、医生、航天政策专家、商业航天从业者……
这些同样是很酷、很有价值的职业。理想的意义不只是终点，更是让你变成更好的人。

**7. 现在可以做的第一步**
- 查一下**中国载人航天工程办公室**或**空军招飞**的官方信息。
- 制定一个“身体+学业+经历”的三年计划。
- 找一位你敬佩的航天员传记读一读，比如杨利伟、王亚平、Chris Hadfield 的书。

如果你愿意告诉我你现在是初中、高中还是大学，以及你的身体和学业情况，我可以帮你列一个更具体的行动清单。加油，星空在等你！
    '"""
    #print("摘要如下：")
    #print(summary_text(summary_text_1))
    #print("成功===========================================================")
    print("测试translate_and_summary =========================================")
    example  = {"text":summary_text_1,"target_lang":"English"}
    print(translate_and_summary(example))



