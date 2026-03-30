# DevMate - 智能编程助手

DevMate 是一个 AI 驱动的智能编程助手项目，旨在基于高级 Agent 系统框架帮助开发者自动化地生成多文件项目、修改代码库及解决编程问题。项目集成了模型上下文协议（MCP）、检索增强生成（RAG）以及 Agent 技能系统，打造全能的开发工作流。

## 🎯 核心特性

- **Agent 工作流**: 利用 LangChain / LangGraph 构建的智能体，能够自主决策网络搜索、文档查阅和代码生成的时机。
- **基于 MCP 的网络搜索**: 通过 Streamable HTTP 协议连接 MCP Tools（集成 Tavily）。当大模型缺乏最新或特定领域知识时，可实时触发 MCP 检索补充信息。
- **结合 RAG 的知识引擎**: 自动解析并向量化 `docs/` 目录下的本地文档内容，在对应语境下动态检索并精准注入到 LLM 的上下文中。
- **Agent Skills (技能复用)**: 具备可扩展的技能学习与调用能力，可将复杂的任务执行模式抽象沉淀为独立的 Skill，统一持久化存储于 `.skills` 目录。
- **全面可观测性**: 原生集成 LangSmith 监控体系，详细记录每一次对话追踪、思维链（Chain of Thought）与底层工具调用情况。
- **极简且严谨的工程范式**: 
  - 所有 Python 代码严格遵守 **PEP 8** 规范。
  - 彻底摒弃 `print`，全局采用 `loguru` 保证标准且规范的日志输出（违禁使用视为严重违规）。
  - 基于业界领先的 `uv` 构建标准 Python 包（支持 `hatchling` 构建系统），高效管理依赖包与环境。

## ⚙️ 环境依赖

- **Python**: `>= 3.13`
- **包管理工具**: [uv](https://docs.astral.sh/uv/)

## 🛠️ 配置说明

项目所有的核心配置均通过根目录下的 `config.toml` 文件进行集中管理。在使用前请准备并正确配置好相关变量：

```toml
[model]
ai_base_url = "你的API基础地址"
api_key = "你的LLM_API_KEY"
model_name = "对话大模型名称"
embedding_model_name = "嵌入大模型名称"

[search]
tavily_api_key = "你的Tavily_API_KEY"

[langsmith]
langchain_tracing_v2 = "true"
langchain_api_key = "你的LangSmith_API_KEY"

[skills]
skills_dir = ".skills"

[vectorstore]
persist_directory = "./chroma_db"
```

## 🚀 启动与部署

### 依赖安装与本地运行

该项目采用标准的 Python `src` 打包规范。

1. 使用 `uv` 同步项目依赖和环境（自动将 `devmate` 注册为内联包）：
   ```bash
   uv sync
   ```
2. 启动 DevMate 主控 CLI 终端：
   ```bash
   uv run python -m src.search_server

   uv run python main.py
   ```
   *(启动后，系统将自动加载并摄入 `docs/` 下的指南和文档知识，进入交互环境并等待输入。)*

### 通过 Docker 容器架构运行

本项目提供原生容器化环境支持，通过 Docker Compose 可以一键无缝拉起包含独立 MCP 检索服务组件和主 Agent 系统架构在内的工作流：

```bash
docker compose up --build
```
*提示：Docker 环境下会自动挂载当前环境的 `config.toml`、模型库目录等核心持久化数据。*

## 📂 核心代码结构

为了符合现代 Python 项目和 PEP 621 标准，应用核心被封装在 `src/devmate/` 极简包结构内。

```text
├── .skills/                   # Agent 技能文件保存目录
├── chroma_db/                 # 本地向量数据库持久化目录
├── docs/                      # RAG 本地知识文档和开发资料存放处
│   ├── assets/                # README 和相关文档的静态资源 (如配图)
│   └── internal_fastapi_guidelines.md
├── src/
│   └── devmate/               # DevMate 系统基础包代码
│       ├── __init__.py        
│       ├── agent.py           # 核心 Agent 行为逻辑与工具加载抽象层
│       ├── config.py          # TOML 配置解析加载器
│       ├── logger.py          # 日志统一管理模块 (基于 loguru封装)
│       ├── rag.py             # 知识文档切分、检索及向量化控制器
│       ├── search_server.py   # MCP (Streamable HTTP) 搜索微服务端
│       └── skills.py          # Agent Skills 生命周期管理
├── tests/                     # 测试用例目录
│   └── test_mcp.py            # MCP 链路可用性验证脚本
├── config.toml                # 全局环境及应用配置常量文件
├── main.py                    # 启动应用和人机交互的主入口点
├── pyproject.toml             # uv 项目描述及构建依赖配置 (Hatchling)
├── Dockerfile                 # 生产级应用镜像构建描述
└── docker-compose.yml         # 多微服务(含 MCP 宿主)组合部署文件
```
