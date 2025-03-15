"""
API客户端
用于连接Cloudflare Worker API
"""

import logging
import json
import time
from typing import Dict, Any, List, Optional

import requests
from requests.exceptions import RequestException

# 配置日志
logger = logging.getLogger("api_client")

class WorkerApiClient:
    """Cloudflare Worker API客户端"""
    
    def __init__(self, base_url: str, timeout: int = 60, max_retries: int = 3):
        """初始化API客户端
        
        Args:
            base_url: API基础URL
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
        """
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        
        logger.info(f"初始化API客户端: URL={base_url}, 超时={timeout}秒")
    
    def _make_request(self, method: str, endpoint: str, params: Dict = None, data: Dict = None) -> Dict:
        """发送API请求
        
        Args:
            method: HTTP方法 (GET, POST等)
            endpoint: API端点
            params: URL参数
            data: 请求体数据
            
        Returns:
            API响应数据
            
        Raises:
            Exception: 请求失败
        """
        url = f"{self.base_url}/{endpoint}"
        
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"发送{method}请求: {url}")
                
                if method.upper() == "GET":
                    response = self.session.get(url, params=params, timeout=self.timeout)
                elif method.upper() == "POST":
                    response = self.session.post(url, params=params, json=data, timeout=self.timeout)
                else:
                    raise ValueError(f"不支持的HTTP方法: {method}")
                
                response.raise_for_status()
                
                return response.json()
            
            except RequestException as e:
                logger.warning(f"请求失败 (尝试 {attempt+1}/{self.max_retries}): {str(e)}")
                
                if attempt == self.max_retries - 1:
                    logger.error(f"达到最大重试次数，请求失败: {url}")
                    raise Exception(f"API请求失败: {str(e)}")
                
                # 指数退避重试
                time.sleep(2 ** attempt)
    
    def get_all_prompts(self) -> List[Dict[str, Any]]:
        """获取所有提示词
        
        Returns:
            提示词列表
        """
        try:
            logger.info("获取所有提示词...")
            response = self._make_request("GET", "prompts")
            
            if not response or not isinstance(response, list):
                logger.warning(f"API返回了无效的提示词列表: {response}")
                return []
            
            logger.info(f"成功获取提示词列表: 共{len(response)}个")
            return response
        
        except Exception as e:
            logger.error(f"获取提示词列表失败: {str(e)}")
            raise
    
    def get_prompt_by_name(self, name: str) -> Dict[str, Any]:
        """根据名称获取提示词
        
        Args:
            name: 提示词名称
            
        Returns:
            提示词数据
            
        Raises:
            Exception: 未找到提示词或请求失败
        """
        try:
            logger.info(f"通过名称获取提示词: {name}")
            
            # 获取所有提示词
            all_prompts = self.get_all_prompts()
            
            # 查找匹配的提示词
            for prompt in all_prompts:
                if prompt.get("name") == name:
                    logger.info(f"找到提示词: {name}")
                    return prompt
            
            # 未找到提示词
            logger.warning(f"未找到名称为 \"{name}\" 的提示词")
            raise Exception(f"未找到名称为 \"{name}\" 的提示词")
        
        except Exception as e:
            logger.error(f"获取提示词失败: {str(e)}")
            raise