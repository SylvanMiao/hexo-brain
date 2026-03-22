## 目前做了什么--0322

使用 FastAPI 搭建了基础后端（main.py）

包含：
静态文件挂载（static/），首页和聊天页面路由。
基于 users.json + .env 的简单用户管理（加载/保存、注册/登录接口）。
/api/chat 接口存在，但只是返回占位字符串（未接入检索或LLM）。
代码结构清晰，适合在此基础上接入RAG。

## 下面要做什么

- [x] 在新环境准备（虚拟环境、依赖、.env）。
- [x] 抽取博客文本（从 static/ 或 blog/ 文件夹读取 HTML/Markdown 并清洗）。
- [ ] 切分长文本（chunking，保持上下文）。
- [ ] 计算向量嵌入并构建向量库（可选：FAISS/Chroma；这里给出基于 sentence-transformers + numpy 的轻量实现）。
- [ ] 提供索引构建/刷新接口（启动时或手动触发）。
- [ ] 查询时先检索 top-k 文档，再将检索到的上下文与用户问题一起发送给 LLM，生成最终答案。
- [ ] 持久化索引（文件保存），并考虑安全（API Key、访问控制）与测试。

## 在 Windows 新环境中的快速命令

启动与退出虚拟环境：
```
#创建虚拟环境
python -m venv venv
.\venv\Scripts\Activate.ps1
#退出环境
deactivate
```
安装最少依赖：
```
pip install fastapi uvicorn python-dotenv sentence-transformers numpy
```


启动:
``` 
uvicorn main:app --reload
```

