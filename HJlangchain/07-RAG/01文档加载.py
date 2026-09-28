"""
LangChain 文档加载：PDF / Markdown / TXT / 网页

核心概念：
    Document  = page_content(正文) + metadata(元信息)，所有加载器统一返回 List[Document]
    load()    = 一次性全部读入内存（适合小文件）
    lazy_load() = 逐页/逐块读入（适合大文件，不爆内存）

依赖：
    pip install pypdf beautifulsoup4 unstructured langchain-text-splitters
"""

import os
import re
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

DEFAULT_USER_AGENT = "Mozilla/5.0 (compatible; LangChainBot/1.0)"

# langchain_community 在导入时会检查这个环境变量，缺了就打 warning
os.environ.setdefault("USER_AGENT", DEFAULT_USER_AGENT)

# 存放待解析的示例文件
BASE_DIR = Path(__file__).resolve().parent
SAMPLE_DIR = BASE_DIR / "sample_docs"
SAMPLE_DIR.mkdir(exist_ok=True)


# ============================================================
# 1. 四种格式的加载器，各自怎么用
# ============================================================

def load_pdf(path: str, password: Optional[str] = None) -> List[Document]:
    """加载 PDF。返回的 Document 数量 = 页数，metadata 里带 page(页码,0起) / source。"""
    from langchain_community.document_loaders import PyPDFLoader

    loader = PyPDFLoader(path, password=password)  # 加密 PDF 传 password
    return loader.load()


def load_txt(path: str, encoding: str = "utf-8") -> List[Document]:
    """加载纯文本。整个文件 = 1 个 Document。"""
    from langchain_community.document_loaders import TextLoader

    # autodetect_encoding=True 会自己猜编码，兜住 GBK/UTF-8 混用的中文 txt
    loader = TextLoader(path, encoding=encoding, autodetect_encoding=True)
    return loader.load()


def load_md(path: str, mode: str = "elements") -> List[Document]:
    """
    加载 Markdown
    :param mode: "elements" 按标题层级拆成多个 Document（默认，保留结构）
                 "raw"      整份当纯文本，返回 1 个 Document
    """
    text = Path(path).read_text(encoding="utf-8")

    if mode == "raw":
        return [Document(page_content=text, metadata={"source": str(path)})]

    return _parse_markdown_elements(text, str(path))


def _parse_markdown_elements(text: str, source: str) -> List[Document]:
    """
    自带的轻量 Markdown 解析：把文档按标题切成一个个「元素」。
    好处是不依赖 unstructured / markdown 包，metadata 里能看到标题层级。
    """
    docs: List[Document] = []
    heading_re = re.compile(r"^(#{1,6})\s+(.+)$")

    current_heading, buffer, level = None, [], 0

    def flush():
        """把缓冲区内容收成一个 Document"""
        content = "\n".join(buffer).strip()
        if not content:
            return
        docs.append(
            Document(
                page_content=content,
                metadata={
                    "source": source,
                    "heading": current_heading or "(无标题)",  # 所属标题
                    "heading_level": level,                     # 标题深度，0 表示正文开头
                },
            )
        )

    for line in text.splitlines():
        match = heading_re.match(line)
        if match:
            flush()                                   # 遇到新标题，先把上一段收尾
            buffer = []
            level = len(match.group(1))
            current_heading = match.group(2).strip()
            buffer.append(line)                       # 标题本身也保留在正文里
        else:
            buffer.append(line)

    flush()  # 收尾最后一段
    return docs


# 网页里这些标签的内容对 RAG 没价值（导航、页脚、脚本、样式）
# 不清掉的话，向量库里会塞满 "Copyright 2024" 这类垃圾文本，污染检索结果
NOISE_TAGS = ["script", "style", "nav", "header", "footer", "aside", "noscript", "iframe", "form"]


def clean_html(html: str) -> str:
    """
    HTML -> 干净纯文本：删噪音标签 + 抽正文 + 压缩空白
    注：WebBaseLoader 的 default_parser 参数只接受解析器名字符串（html.parser/lxml...），
        塞不了自定义函数，所以这里用子类覆写 lazy_load 的方式接入。
    """
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(NOISE_TAGS):        # 找到所有噪音标签并从 DOM 里摘掉
        tag.decompose()

    # separator="\n" 保留换行结构，切分器才能识别段落边界
    lines = [ln.strip() for ln in soup.get_text(separator="\n").splitlines()]
    return "\n".join(ln for ln in lines if ln)   # 顺手丢掉空行


def _build_clean_web_loader(url: str):
    """构造一个会先清洗 HTML 的 WebBaseLoader 子类实例"""
    from langchain_community.document_loaders import WebBaseLoader

    class CleanWebLoader(WebBaseLoader):
        def lazy_load(self):
            from bs4 import BeautifulSoup

            for path in self.web_paths:
                # UA 等 header 在父类 __init__ 里已写进 self.session.headers，这里直接 get
                response = self.session.get(path)
                response.raise_for_status()
                html = response.text

                soup = BeautifulSoup(html, "html.parser")
                title = soup.title
                yield Document(
                    page_content=clean_html(html),
                    metadata={
                        "source": path,
                        "title": title.get_text().strip() if title else "",
                    },
                )

    # 必须伪装 UA，否则很多站点（含 langchain 文档站）直接返回 403
    # 参数名有版本差异：老版本 user_agent=，0.3+ 改成 header_template=
    return CleanWebLoader(url, header_template={"User-Agent": DEFAULT_USER_AGENT})


def load_web(url: str, clean: bool = True) -> List[Document]:
    """
    加载网页，HTML 自动转纯文本
    :param clean: True 剔除导航/页脚等噪音（默认）；False 用 WebBaseLoader 内置解析
    """
    from langchain_community.document_loaders import WebBaseLoader

    if clean:
        return _build_clean_web_loader(url).load()

    return WebBaseLoader(
        url,
        header_template={"User-Agent": DEFAULT_USER_AGENT},
        bs_get_text_kwargs={"separator": "\n"},
    ).load()


# ============================================================
# 2. 统一入口：不管传 PDF / MD / TXT / 网址，都用这一个函数
# ============================================================

# 后缀 -> 加载函数 的映射表，想支持新格式只要往里加一行
LOADERS = {
    ".pdf": load_pdf,
    ".md": load_md,
    ".markdown": load_md,
    ".txt": load_txt,
    ".text": load_txt,
}


def load_document(source: str) -> List[Document]:
    """
    智能分发加载器
    :param source: 本地文件路径 或 http(s) 网页地址
    """
    if source.startswith(("http://", "https://")):
        return load_web(source)

    path = Path(source)
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {path}")

    suffix = path.suffix.lower()
    if suffix not in LOADERS:
        raise ValueError(f"暂不支持的格式: {suffix}，当前支持: {list(LOADERS)} 或网页地址")

    return LOADERS[suffix](str(path))


# ============================================================
# 3. 大文件用 lazy_load 逐页读，避免一次性撑爆内存
# ============================================================

def load_pdf_lazy(path: str):
    """PDF 专用：生成器，一次读一页。几千页的 PDF 必须这么读。"""
    from langchain_community.document_loaders import PyPDFLoader

    yield from PyPDFLoader(path).lazy_load()


# ============================================================
# 4. 加载完要切分，才能喂给 LLM（超出上下文就丢内容/报错）
# ============================================================

def split_documents(docs: List[Document], chunk_size: int = 500, chunk_overlap: int = 50) -> List[Document]:
    """
    递归字符切分：优先按段落 -> 行 -> 句子边界切，尽量不破坏语义
    :param chunk_overlap: 相邻块重叠字数，防止答案正好被切断
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", "。", "！", "？", ".", " ", ""],  # 优先级从高到低
        keep_separator=True,
    )
    return splitter.split_documents(docs)


# ============================================================
# 5. 打印工具
# ============================================================

def preview(docs: List[Document], n: int = 2, chars: int = 200) -> None:
    """打印前 n 个 Document 的正文片段和元信息"""
    print(f"共 {len(docs)} 个 Document")
    for i, doc in enumerate(docs[:n]):
        text = doc.page_content.strip().replace("\n", " ")
        print(f"\n--- [{i}] {text[:chars]}{'...' if len(text) > chars else ''}")
        print(f"    metadata: {doc.metadata}")


# ============================================================
# 6. 造点测试数据，保证脚本能直接跑
# ============================================================

def make_samples() -> dict:
    """生成示例 txt / md；PDF 和网页用现成的，不造假数据。"""
    txt_path = SAMPLE_DIR / "demo.txt"
    txt_path.write_text(
        "LangChain 文档加载器\n"
        "====================\n"
        "DocumentLoader 的作用是把非结构化数据（PDF/Word/网页/数据库）转成 Document 对象。\n"
        "每个 Document 包含 page_content 和 metadata 两个字段。\n"
        "切分器负责把长文档切成小块，交给向量模型做 Embedding。\n",
        encoding="utf-8",
    )

    md_path = SAMPLE_DIR / "demo.md"
    md_path.write_text(
        "# RAG 入门\n\n"
        "## 什么是 RAG\n"
        "检索增强生成（Retrieval-Augmented Generation），先检索再生成，缓解模型幻觉。\n\n"
        "## 三个核心组件\n"
        "1. Document Loader：加载原始文档\n"
        "2. Text Splitter：切分文档\n"
        "3. Vector Store：存储向量并做相似度检索\n",
        encoding="utf-8",
    )
    return {"txt": str(txt_path), "md": str(md_path)}


# ============================================================
# 7. 演示
# ============================================================

if __name__ == "__main__":
    samples = make_samples()

    # --- 7.1 TXT ---
    print("=" * 60, "\n【1】加载 TXT\n")
    txt_docs = load_txt(samples["txt"])
    preview(txt_docs)

    # --- 7.2 Markdown ---
    print("\n" + "=" * 60, "\n【2】加载 Markdown（mode=elements，能看到标题层级）\n")
    md_docs = load_md(samples["md"])
    preview(md_docs, n=3)

    # --- 7.3 PDF（需自行放入一个 pdf 文件）---
    print("\n" + "=" * 60, "\n【3】加载 PDF\n")
    pdf_path = SAMPLE_DIR / "demo.pdf"
    if pdf_path.exists():
        pdf_docs = load_pdf(str(pdf_path))
        preview(pdf_docs)
        print(f"\n[懒加载] 逐页读取前 2 页:")
        for i, doc in enumerate(load_pdf_lazy(str(pdf_path))):
            if i >= 2:
                break
            print(f"  第 {doc.metadata.get('page')} 页: {doc.page_content[:80]}...")
    else:
        print(f"未找到 {pdf_path}，把任意 pdf 放进去再跑本节即可。")
        print("代码写法：load_pdf('demo.pdf')  ->  返回 N 个 Document（N=页数）")

    # --- 7.4 网页 ---
    print("\n" + "=" * 60, "\n【4】加载网页\n")
    try:
        web_docs = load_web("https://python.langchain.com/docs/concepts/text_splitters/")
        preview(web_docs)
    except Exception as e:
        print(f"网页加载失败（可能是网络不通）：{type(e).__name__}: {e}")

    # --- 7.5 统一入口 ---
    print("\n" + "=" * 60, "\n【5】统一入口 load_document() 自动判断格式\n")
    for src in [samples["txt"], samples["md"]]:
        print(f"{Path(src).name} -> {len(load_document(src))} 个 Document")

    # --- 7.6 切分 ---
    print("\n" + "=" * 60, "\n【6】切分成块（chunk=120, overlap=20）\n")
    chunks = split_documents(txt_docs, chunk_size=120, chunk_overlap=20)
    print(f"1 个 Document({len(txt_docs[0].page_content)} 字) -> {len(chunks)} 个 chunk")
    for i, c in enumerate(chunks):
        print(f"  [{i}] {c.page_content[:70]!r}")
