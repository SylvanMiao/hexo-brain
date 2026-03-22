---
title: FastAPI 入门教程
date: 2024-01-15
tags: [Python, FastAPI, API]
categories: 教程
---

# FastAPI 入门教程

## 什么是 FastAPI

FastAPI 是一个用于构建 API 的 Python 框架。它具有以下特点：

- **快速**：性能接近 Node.js 和 Go
- **自动文档**：自动生成 Swagger UI 文档
- **类型检查**：利用 Python 类型提示，自动验证数据
- **异步支持**：原生支持 async/await

## 安装 FastAPI

使用 pip 安装：

```bash
pip install fastapi uvicorn
```

## 第一个 FastAPI 应用

创建一个简单的 API：

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}
```

运行服务：

```bash
uvicorn main:app --reload
```

## 总结

FastAPI 是一个现代化的 Web 框架，非常适合构建 AI 应用和微服务。
