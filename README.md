# AI Agent 学习仓库

基于 **LangChain / LangGraph** 的 AI Agent 学习练习记录，从模型对接一路练到 Agent 工具调用与会话记忆。

## 学习路线

```
模型对接 → 流式输出 → 多轮对话 → Agent + 自定义工具 → 短期记忆
```

## 目录结构

```
ai-agent/
├── HJnice/
│   └── langchain/              # LangChain 基础
│       ├── test.py                    # Tongyi LLM 基本调用 + 流式输出
│       ├── 聊天模型对接.py             # ChatTongyi 聊天模型，System/User 消息
│       └── 1.实现多轮对话.py           # 封装 multiTurnChat 类，手动维护对话历史
└── HJlangchain/                # LangChain Agent 进阶
    ├── 01.py                          # create_agent + @tool 自定义工具（天气/时间），DeepSeek
    ├── 02.py                          # 多工具协作（排班/日期/天气），Kimi（火山方舟）
    ├── 03短期记忆.py                   # InMemorySaver checkpointer + thread_id 会话记忆
    ├── 04memory_store.py              # InMemoryStore 长期记忆（待补充）
    ├── langsmith/                     # LangSmith 可观测性
    │   ├── 01langsmith.py             # @traceable 装饰器追踪 LLM 调用
    │   └── 02operation.py             # @traceable + metadata/tags 追踪 Prompt 链路
    └── agent/
        └── function_calling.py        # OpenAI SDK 原生 Function Calling（航班查询/票价查询），火山方舟
```

## 环境准备

- Python 3.10+

安装依赖：

```bash
pip install langchain langchain-openai langchain-community langgraph python-dotenv
```

## 配置密钥

先复制模板文件并填入自己的密钥：

```bash
cp .env.example .env
```

各变量用途：

| 变量 | 用途 | 使用脚本 |
|------|------|----------|
| `dashscope_API_KEY` | 通义千问 DashScope | `HJnice/langchain/` 全部 |
| `DS_API_KEY` / `DS_URL` | DeepSeek | `HJlangchain/01.py` |
| `FZ_API_KEY` / `FZ_BASE_URL` | 火山方舟（Kimi） | `HJlangchain/02.py`、`03短期记忆.py`、`agent/function_calling.py` |
| `LANGSMITH_API_KEY` | LangSmith 追踪 | `HJlangchain/langsmith/` 全部 |

> `.env` 已加入 `.gitignore`，不会提交到仓库。

## 运行示例

```bash
# 基础：通义千问流式输出
python HJnice/langchain/2.test.py

# 基础：聊天模型 + System Prompt
python "HJnice/langchain/聊天模型对接.py"

# 基础：多轮对话封装类
python "HJnice/langchain/1.实现多轮对话.py"

# Agent：自定义工具调用（问"北京今天天气怎么样"看效果）
python HJlangchain/01.py

# Agent：多工具协作（问"我明天需要上班吗，需不需要带伞"看效果）
python HJlangchain/02.py

# Agent：短期记忆（同一 thread_id 内多轮追问"我今天该做啥来着"）
python HJlangchain/03短期记忆.py

# LangSmith：@traceable 追踪 LLM 调用（到 smith.langchain.com 查看 Trace）
python HJlangchain/langsmith/01langsmith.py

# Function Calling：OpenAI SDK 原生工具调用（问"查北京到上海的航班"看效果）
python HJlangchain/agent/function_calling.py
```

## 知识点速记

| 脚本 | 核心知识点 |
|------|-----------|
| `2.test.py` | `Tongyi` LLM 的 `invoke` / `stream` |
| `3.聊天模型对接.py` | `ChatTongyi`，消息角色（system / user），`stream` 逐块打印 |
| `1.实现多轮对话.py` | 用类封装对话历史，`yield` 实现生成器式流式回复 |
| `01.py` | `create_agent` 创建 Agent，`@tool()` 定义工具，docstring 即工具描述 |
| `02.py` | `@tool(名称, description)` 自定义工具名与描述，多工具按需调度 |
| `03短期记忆.py` | `InMemorySaver` + `configurable.thread_id` 实现会话级记忆；`stream_mode="messages"` 流式输出 |
| `01langsmith.py` | `LANGSMITH_TRACING` 环境变量开启追踪，`@traceable(run_type="llm")` 装饰函数 |
| `02operation.py` | `@traceable(metadata=..., tags=...)` 给 Trace 打标签，PromptTemplate 链路追踪 |
| `agent/function_calling.py` | OpenAI SDK `tools` 参数定义 JSON Schema 工具；模型返回 `tool_calls` 后本地执行函数、以 `role="tool"` + `tool_call_id` 回填结果再二次请求 |

## 待补充

- [ ] `04memory_store.py`：`InMemoryStore` 跨会话长期记忆
