# lingyu — 领域智能客服对话模块

基于 LangChain 的电商智能客服对话系统。核心思路是**意图识别 → 意图路由 → 分角色提示词 → 大模型生成**，并配套一套多轮对话记忆管理（对话历史 + 滚动摘要 + 关键事实插槽）。

## 功能特性

- **意图识别（结构化输出）**：通过 Pydantic 结构化输出（`with_structured_output`）让模型返回意图列表、插槽（slots）和置信度，解析失败自动重试一次，仍失败则走低置信度兜底。
- **低置信度兜底**：置信度 ≤ `0.3` 时不调用主模型，直接返回引导话术（提示用户选择：查物流 / 改地址 / 退货退款 / 投诉）。
- **意图路由**：按意图切换不同的 system prompt（物流查询、修改地址、退货退款、投诉处理、通用闲聊）。
- **多轮记忆管理**：由 `Memory` 整合三个独立管理器——
  - `ChatHistoryManager`：会话消息历史（内存存储）
  - `SummaryManager`：每累计 12 条消息触发一次增量摘要，压缩历史上下文
  - `FactsManager`：存储关键事实（如订单号、地址等插槽值），每轮随消息一起注入上下文
- **统一日志**：每轮请求记录 trace_id、意图、置信度、耗时（正常记 info，异常记 error）。
- **环境变量自动加载**：`core/env_loader.py` 从模块根目录逐级向上查找 `.env`，不依赖当前工作目录。

## 目录结构

```
lingyu/
├── chat_servers.py                  # 入口：ChatServers 类，handle() 为主流程
├── config.py                        # 模型配置（意图识别用 qwen-flash，主模型 qwen3-max）
├── core/
│   ├── protocol.py                  # ChatRequest / ChatResponse 数据类
│   ├── intent_recognizer_with_strutured_output.py  # 意图识别器（Pydantic 结构化输出）
│   ├── memory.py                    # 记忆管理：整合历史 / 摘要 / 事实三个管理器
│   ├── chat_history_manager.py      # 对话历史管理（InMemory，按 session_id 隔离）
│   ├── summary_manager.py           # 滚动摘要管理（批次阈值 12 条）
│   ├── facts_manager.py             # 关键事实（slots）存储
│   ├── prompt.py                    # 意图识别 / 摘要生成的 Prompt 模板
│   └── env_loader.py                # .env 向上查找加载工具
└── test/
    ├── 2.测试结构化输出.py
    ├── 3.测试chat_servers.py        # 单轮请求测试
    └── 4.测试多轮对话.py
```

## 请求处理流程

`ChatServers.handle(request)` 的执行顺序：

```
1. 按 chat_session_id 获取/创建 Memory
2. 意图识别：基于用户输入 + 最近 6 条历史消息，输出 intents / slots / confidence
3. confidence <= 0.3 → 直接返回兜底引导话术
4. 取主意图（intents[0]），映射到对应的 system prompt
5. 准备上下文：关键事实 + 历史摘要 + 未摘要的最近消息
6. prompt | llm | StrOutputParser 链式调用生成回复
7. 用户消息、AI 回复写回历史，并累计摘要计数（达到阈值自动增量摘要）
8. 用识别出的 slots 更新关键事实
9. 记录日志，返回 ChatResponse
```

任何环节抛出异常都会被捕获、记入日志，并返回兜底文案「抱歉，系统暂时开小差了」，不会向上抛出。

## 快速开始

### 1. 配置环境变量

在 `lingyu/` 目录（或其任意上级目录）放置 `.env`：

```
DASHSCOPE_API_KEY=你的通义千问APIKey
```

也可以在初始化时直接传入：

```python
chat_service = ChatServers(api_key="sk-xxx")
```

### 2. 发起一次对话

```python
import uuid
from chat_servers import ChatServers
from core.protocol import ChatRequest

chat_service = ChatServers()

request = ChatRequest(
    user_id="user_001",
    chat_session_id="session_001",          # 同一会话保持一致即可延续多轮记忆
    trace_id=str(uuid.uuid4()),
    user_input="我的快递到哪了？我的订单号是7856757536124",
    api_key="",                              # 也可留空，走环境变量
)

response = chat_service.handle(request)
print(response.response)
```

多轮对话时复用同一个 `chat_session_id`，模块会自动维护历史、摘要与关键事实。

### 3. 运行测试

```bash
python test/3.测试chat_servers.py
```

## 模型配置

在 `config.py` 中调整：

| 配置项 | 默认值 | 用途 |
|---|---|---|
| `INTENT_RECOGNIZER_MODEL` | `qwen-flash` | 意图识别（轻量、快） |
| `DASHSCOPE_MODEL` | `qwen3-max` | 主对话模型 |

## 已支持的意图

| 意图名 | 说明 |
|---|---|
| `track_shipping` | 查询物流进度（需要订单号/运单号） |
| `change_address` | 修改收货地址（需要订单号 + 新地址，先确认是否已发货） |
| `refund` | 申请退货退款 |
| `complaint` | 投诉建议 |
| `general` | 兜底通用对话 |

## 如何新增一个意图

1. 在 `core/prompt.py` 的意图识别 Prompt 中补充新意图的定义与插槽说明；
2. 在 `chat_servers.py` 的 `_system_prompt_by_intent()` 映射表中为新意图添加对应的 system prompt；
3. 如需特殊处理（如低置信度引导菜单），在 `handle()` 流程中扩展。

## 已知限制

- 消息历史、摘要、事实均存储在**进程内存**中，服务重启后会话状态丢失；
- 当前只路由**单意图**（取 `intents[0]`），复合意图未拆分处理；
- 依赖阿里云 DashScope（`ChatTongyi`），如需切换其他模型供应商，替换 `ChatTongyi` 即可，接口均基于 `BaseChatModel` 抽象。
