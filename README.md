# MCP提示词管理服务

基于Model Context Protocol的Python SDK实现的提示词管理服务。

## 功能

- 连接Cloudflare Worker API获取提示词数据
- 提供MCP接口供Claude、Cursor等AI助手调用
- 包含可靠的重试、超时和缓存机制

## 安装

```bash
pip install mcp-prompt-manager
```

## 使用方法

### 命令行启动

```bash
mcp-prompt-manager
```

### 在Claude Desktop或Cursor中配置

1. 安装包后，在Claude Desktop或Cursor的MCP服务配置中添加：
   - 名称：作图 prompt
   - 类型：command
   - 命令：mcp-prompt-manager

2. 使用以下工具：
   - `mcp__get_all_names` - 获取所有提示词名称
   - `mcp__get_content_by_name` - 获取特定提示词内容

## 配置选项

可以通过环境变量配置：

```bash
# 设置Worker URL
export MCP_WORKER_URL="https://your-worker-url.workers.dev"

# 设置超时时间（秒）
export MCP_API_TIMEOUT=60

# 设置重试次数
export MCP_RETRIES=3
```

## 代理配置

如需使用代理，可设置以下环境变量:

```bash
# Linux/Mac
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890

# Windows
set HTTP_PROXY=http://127.0.0.1:7890
set HTTPS_PROXY=http://127.0.0.1:7890
```

## 开发

```bash
# 克隆仓库
git clone https://github.com/Ceeon/mcp-prompt-manager.git
cd mcp-prompt-manager

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装开发依赖
pip install -e ".[dev]"
```

## 许可证

MIT