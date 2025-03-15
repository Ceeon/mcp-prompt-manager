"""
MCP 服务器
基于Model Context Protocol的Python SDK实现
"""

import logging
import os
import json
import argparse
import sys
from typing import Dict, Any, List, Optional

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("错误: 未找到MCP库，请先安装依赖: pip install mcp")
    print("如果您在虚拟环境中运行，请确保已激活虚拟环境")
    import sys
    sys.exit(1)

from .api_client import WorkerApiClient

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("mcp_server")

# 默认配置选项
DEFAULT_CONFIG = {
    "WORKER_URL": "https://polished-math-2b32.zhongce-xie.workers.dev",
    "API_TIMEOUT": 60,  # 秒
    "RETRIES": 3,
}

# 从环境变量读取配置
def load_config_from_env():
    """从环境变量加载配置"""
    config = DEFAULT_CONFIG.copy()
    
    if os.environ.get("MCP_WORKER_URL"):
        config["WORKER_URL"] = os.environ.get("MCP_WORKER_URL")
    
    if os.environ.get("MCP_API_TIMEOUT"):
        try:
            config["API_TIMEOUT"] = int(os.environ.get("MCP_API_TIMEOUT"))
        except ValueError:
            logger.warning(f"无效的API超时值: {os.environ.get('MCP_API_TIMEOUT')}, 使用默认值: {DEFAULT_CONFIG['API_TIMEOUT']}")
    
    if os.environ.get("MCP_RETRIES"):
        try:
            config["RETRIES"] = int(os.environ.get("MCP_RETRIES"))
        except ValueError:
            logger.warning(f"无效的重试次数: {os.environ.get('MCP_RETRIES')}, 使用默认值: {DEFAULT_CONFIG['RETRIES']}")
    
    return config

# 加载配置
CONFIG = load_config_from_env()

# 创建MCP服务器
mcp = FastMCP("作图 Prompt 管理服务")

def initialize():
    """初始化API客户端"""
    logger.info(f"启动配置: WORKER_URL={CONFIG['WORKER_URL']}, API_TIMEOUT={CONFIG['API_TIMEOUT']}秒")
    
    # 创建API客户端
    api_client = WorkerApiClient(CONFIG["WORKER_URL"], CONFIG["API_TIMEOUT"], CONFIG["RETRIES"])
    return api_client

# 初始化API客户端
api_client = initialize()

@mcp.tool()
def mcp__get_all_names() -> Dict[str, Any]:
    """获取所有提示词的名称
    
    Returns:
        JSON格式的提示词名称列表
    """
    try:
        logger.info("获取所有提示词名称...")
        
        all_prompts = api_client.get_all_prompts()
        logger.info(f"成功获取提示词列表: 共{len(all_prompts)}个")
        
        names = [p.get("name") for p in all_prompts]
        
        result = {
            "status": "success",
            "message": "成功获取所有提示词名称",
            "data": names
        }
        
        logger.info("返回提示词名称列表")
        return result
    except Exception as e:
        logger.error(f"获取提示词名称出错: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        
        error_result = {
            "status": "error",
            "message": f"获取所有提示词名称失败: {str(e)}"
        }
        
        return error_result

@mcp.tool()
def mcp__get_content_by_name(name: str) -> Dict[str, Any]:
    """根据名称获取提示词内容
    
    Args:
        name: 提示词名称
        
    Returns:
        提示词详情
    """
    try:
        logger.info(f"通过名称获取提示词内容 (名称: \"{name}\")...")
        
        prompt = api_client.get_prompt_by_name(name)
        logger.info(f"成功获取提示词内容: {name}")
        
        result = {
            "status": "success",
            "message": f"成功获取名称为 \"{name}\" 的提示词内容",
            "data": {
                "id": prompt.get("id"),
                "name": prompt.get("name"),
                "content": prompt.get("content"),
                "category": prompt.get("category", ""),
                "description": prompt.get("description", "")
            }
        }
        
        return result
    except Exception as e:
        logger.error(f"获取提示词内容出错: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        
        error_result = {
            "status": "error",
            "message": f"通过名称获取提示词内容失败: {str(e)}"
        }
        
        return error_result

def print_version():
    """打印版本信息"""
    from . import __version__
    print(f"MCP Prompt Manager v{__version__}")
    print("Copyright (c) 2025 Chengfeng")
    print("MIT License")

def print_config():
    """打印当前配置"""
    print("\n当前配置:")
    print(f"  Worker URL: {CONFIG['WORKER_URL']}")
    print(f"  API 超时: {CONFIG['API_TIMEOUT']}秒")
    print(f"  重试次数: {CONFIG['RETRIES']}")
    
    # 打印代理配置
    http_proxy = os.environ.get("HTTP_PROXY", "未设置")
    https_proxy = os.environ.get("HTTPS_PROXY", "未设置")
    print("\n代理配置:")
    print(f"  HTTP_PROXY: {http_proxy}")
    print(f"  HTTPS_PROXY: {https_proxy}")

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="MCP提示词管理服务 - 基于Model Context Protocol的Python SDK实现",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument("-v", "--version", action="store_true", help="显示版本信息")
    parser.add_argument("--config", action="store_true", help="显示当前配置")
    parser.add_argument("--port", type=int, default=8000, help="服务器端口 (默认: 8000)")
    parser.add_argument("--host", default="127.0.0.1", help="服务器主机 (默认: 127.0.0.1)")
    
    return parser.parse_args()

def main():
    """命令行入口点"""
    args = parse_args()
    
    # 处理版本信息
    if args.version:
        print_version()
        return 0
    
    # 处理配置信息
    if args.config:
        print_version()
        print_config()
        return 0
    
    # 启动服务器
    logger.info("正在启动MCP Prompt管理服务器...")
    logger.info(f"服务器地址: {args.host}:{args.port}")
    
    try:
        mcp.run(host=args.host, port=args.port)
    except Exception as e:
        logger.error(f"启动服务器时出错: {str(e)}")
        return 1
    return 0

# 如果直接运行此脚本，启动MCP服务器
if __name__ == "__main__":
    sys.exit(main())