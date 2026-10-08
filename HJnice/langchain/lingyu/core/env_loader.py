"""环境变量加载公共工具。

统一在此加载项目根目录下的 .env 文件，避免"依赖当前工作目录(CWD)"
导致在 主项目 或 单独打开模块 等不同环境下加载不到环境变量的问题。
"""
from pathlib import Path

from dotenv import load_dotenv

# core/ 所在目录的上级即 lingyu 模块根目录
_CORE_DIR = Path(__file__).resolve().parent
_MODULE_ROOT = _CORE_DIR.parent


def load_env(env_file: str | Path = ".env", *, verbose: bool = False) -> bool:
    """向上查找并加载 .env 文件。

    从 lingyu 模块根目录开始逐级向上，找到最近的 .env 文件并加载。
    这样无论从哪个目录执行脚本，都能加载到 ai-agent 主项目下的 .env。

    查找优先级（就近优先）：
        1. lingyu/ 模块根目录
        2. langchain/ 、HJnice/ 、ai-agent/ …（逐级向上直到磁盘根目录）

    Args:
        env_file: 环境变量文件名，默认 ".env"。
        verbose: 是否打印加载路径，便于调试。

    Returns:
        True 表示成功找到并加载了 .env；False 表示未找到。
    """
    for directory in (_MODULE_ROOT, *_MODULE_ROOT.parents):
        target = directory / env_file
        if target.is_file():
            loaded = load_dotenv(target, override=False)
            if verbose:
                path_display = str(target)
                if loaded:
                    print(f"[env_loader] 已加载环境变量: {path_display}")
                else:
                    print(f"[env_loader] 找到但未加载: {path_display}")
            return loaded
    if verbose:
        print(f"[env_loader] 警告: 向上查找未找到 {env_file} 文件")
    return False
