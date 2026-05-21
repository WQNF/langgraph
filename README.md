# OmniPilot – 企业智能运营助手

基于多智能体协作的企业级 AI 助手，支持自然语言查询公司文档（RAG）、业务数据库（SQL）、代码生成与报告总结。系统采用 LangGraph 实现智能任务规划与调度，集成 Milvus 向量库、PostgreSQL 数据库、JWT 认证、Prometheus + Grafana 监控，并提供流式输出与 Streamlit 交互界面。

## 🏗️ 架构图

```mermaid
flowchart LR
    User[用户] -->|自然语言| Frontend[Streamlit 前端]
    Frontend -->|HTTP SSE 流式| FastAPI[FastAPI 网关]
    FastAPI -->|JWT 解析| Auth[认证模块]
    Auth -->|注入用户部门| Graph[LangGraph 工作流]
    
    Graph --> Planner[Planner 任务规划]
    Planner -->|生成执行计划| Dispatcher[Dispatcher 或 Executor]
    Dispatcher -->|并行/串行调用| Agents[专家智能体]
    
    Agents --> RAG[RAG Agent<br>知识库检索]
    Agents --> SQL[Data Analyst<br>数据库查询]
    Agents --> Researcher[General Researcher<br>通用问答]
    
    RAG --> Milvus[(Milvus 向量库)]
    SQL --> Postgres[(PostgreSQL 业务库)]
    
    Agents -->|结果汇聚| Summarize[Summarize 总结整合]
    Summarize -->|最终答案| Frontend
    
    Prometheus -->|抓取指标| FastAPI
    Grafana -->|可视化| Prometheus
🚀 快速开始
1. 克隆仓库
bash
git clone https://github.com/your-username/omnipilot.git
cd omnipilot
2. 配置环境变量
在项目根目录创建 .env 文件，填入你的 API 密钥（需 DeepSeek 或 SiliconFlow 令牌）：

text
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxx
JWT_SECRET_KEY=请生成一个随机字符串
3. 启动基础服务（Docker）
确保 Docker Desktop 已安装并运行，然后执行：

bash
docker compose up -d
这将启动 PostgreSQL（含向量扩展）、Milvus、Prometheus、Grafana 等所有依赖服务。

4. 初始化数据库与知识库
bash
# 初始化 PostgreSQL 表结构及示例数据
python tools/init_db.py

# 初始化 Milvus 知识库（将 data/documents/ 下的 .txt 文件向量化并存入向量库）
python tools/init_milvus.py
5. 启动后端
bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
6. 启动前端
新开一个终端：

bash
streamlit run frontend/app.py
7. 访问系统
前端界面：http://localhost:8501
登录用户：zhangwei 密码：secret123

Grafana 监控：http://localhost:3000 （admin/admin）

后端 API 文档：http://localhost:8000/docs

📡 API 文档
端点	方法	描述	认证
/token	POST	获取 JWT 访问令牌	无（表单 username/password）
/chat/stream	POST	流式多 Agent 问答	Bearer Token
/metrics	GET	Prometheus 监控指标	无
获取 Token 示例
bash
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=zhangwei&password=secret123"
流式问答示例
bash
curl -X POST "http://localhost:8000/chat/stream" \
  -H "Authorization: Bearer <你的token>" \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"找出王磊销售数量最多的产品，并介绍一下这个产品"}]}'
✨ 主要特性
🧠 多 Agent 协作：专职 Agent 分别处理数据库查询、知识库检索、通用问答，最后由总结 Agent 整合。

🗺️ 智能任务规划：Planner 自动拆解复杂问题，决定并行或串行调用专家，并处理子任务依赖。

📚 企业级 RAG：基于 Milvus 向量数据库 + 语义分块 + BGE‑Reranker 重排序，检索准确率高。

🔐 JWT 认证与数据权限：用户登录后按部门过滤数据，保障信息安全。

📊 Prometheus + Grafana 监控：实时显示 API 请求量、LLM 调用次数、95% 延迟，成本可控。

💬 流式输出与打字机效果：通过 Server‑Sent Events (SSE) 实现实时进度反馈和最终答案。

🐳 Docker 一键部署：所有依赖服务容器化，一条命令即可启动完整后端基座。

🎬 演示视频
建议录制 2‑3 分钟的视频，展示以下场景：

在 Streamlit 登录，获取 Token（过程自动，可提及）。

提问：“找出王磊销售数量最多的产品，并介绍一下这个产品”。

提问：“查询张伟的业绩，并根据公司激励政策计算奖励金额”。

打开 Grafana 面板，显示实时请求量和 LLM 调用次数。

录制工具：OBS Studio（免费）或系统自带录屏。
完成后可上传至 Bilibili 或 YouTube，将链接填入 README 尾部。

🧱 项目结构
text
omnipilot/
├── agents/                # 各智能体节点
│   ├── planner.py
│   ├── dispatcher.py
│   ├── executor.py
│   ├── rag.py
│   ├── data_analyst.py
│   ├── researcher.py
│   ├── summarize.py
│   └── supervisor.py     (备用)
├── tools/                 # 工具封装
│   ├── retriever.py       # Milvus 检索器
│   ├── sql_executor.py    # PostgreSQL 执行器
│   ├── embedder.py        # 嵌入模型
│   ├── reranker.py        # 重排序
│   ├── init_db.py         # 数据库初始化
│   └── init_milvus.py     # 知识库初始化
├── core/                  # 状态定义、图构建、LLM、Metrics
│   ├── state.py
│   ├── graph.py
│   ├── llm.py
│   └── metrics.py
├── api/                   # FastAPI 应用
│   ├── main.py
│   └── dependencies/
│       └── auth.py
├── frontend/              # Streamlit 界面
│   └── app.py
├── config/                # 提示词模板
│   └── prompts.py
├── data/                  # 知识库文档（.txt）
│   └── documents/
├── docker/                # Docker Compose
│   └── docker-compose.yml
├── prometheus/            # Prometheus 配置
│   └── prometheus.yml
└── README.md
📄 许可
本项目基于 MIT License 开源，仅供学习与展示使用。实际企业部署时请替换所有默认密码与密钥。