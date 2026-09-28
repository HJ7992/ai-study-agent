from langchain_core.documents import Document

docs = [
    {
        Document(page_content="LangChain是一个用于构建LLM应用的开源框架。"
                    "它提供了预构建的Agent架构，支持与OpenAI、Anthropic、Google等多家模型集成。"
                    "LangChain的核心组件包括：模型接口、Tool工具、链式编排等。",
                metadata={"source": "langchain_intro.txt", "category": "framework"},
                 ),
        Document(
            page_content="RAG（检索增强生成）是一种增强大语言模型能力的技术。"
                         "它通过在生成回答前从外部知识库检索相关信息，来解决LLM的知识截止和幻觉问题。"
                         "RAG的核心流程包括：文档索引、向量检索、上下文增强生成。",
            metadata={"source": "rag_intro.txt", "category": "technique"}
        ),
        Document(
            page_content="LangSmith是LangChain生态系统中的观测和评估平台。"
                         "它可以帮助开发者追踪Agent执行过程、调试复杂行为、评估输出质量。"
                         "LangSmith支持自动化评估、数据集管理、实验对比等功能。",
            metadata={"source": "langsmith_intro.txt", "category": "platform"}
        )
    }
]