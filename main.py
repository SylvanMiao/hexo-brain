import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 创建 FastAPI 应用实例
app = FastAPI()

# 挂载静态文件目录，用于访问 HTML 文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 用户数据文件路径
USERS_FILE = "users.json"


def load_users():
    """
    加载用户数据
    
    如果 users.json 存在，从文件加载；否则从 .env 读取默认用户并创建文件
    """
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    
    # 从 .env 加载初始用户（格式：用户名：密码，用逗号分隔）
    users_raw = os.getenv("USERS", "admin:123456,user1:abc123")
    users = {}
    for item in users_raw.split(","):
        if ":" in item:
            u, p = item.split(":", 1)
            users[u.strip()] = p.strip()
    
    # 保存初始用户到文件
    save_users(users)
    return users


def save_users(users):
    """
    保存用户数据到 JSON 文件
    
    Args:
        users: 用户字典 {用户名：密码}
    """
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)


# 初始化用户数据
USERS = load_users()


class LoginRequest(BaseModel):
    """登录请求数据模型"""
    username: str
    password: str


class RegisterRequest(BaseModel):
    """注册请求数据模型"""
    username: str
    password: str
    confirm_password: str


class RegisterResponse(BaseModel):
    """注册响应数据模型"""
    success: bool
    message: str

class ChatRequest(BaseModel):
    """聊天请求数据模型"""
    message: str


class ChatResponse(BaseModel):
    """聊天响应数据模型"""
    success: bool
    message: str
    


@app.get("/")
def read_root():
    """
    首页路由
    
    返回登录页面
    """
    return FileResponse("static/login.html")


@app.get("/chat")
def chat_page():
    """
    聊天页面路由
    
    返回聊天页面
    """
    return FileResponse("static/chat.html")


@app.post("/api/login")
def login(request: LoginRequest):
    """
    登录接口
    
    Args:
        request: 登录请求，包含用户名和密码
        
    Returns:
        登录成功返回 success=True
        
    Raises:
        HTTPException: 401 错误，用户名或密码错误
    """
    if request.username in USERS and USERS[request.username] == request.password:
        return {"success": True, "message": "登录成功"}
    else:
        raise HTTPException(status_code=401, detail="用户名或密码错误")


@app.post("/api/register")
def register(request: RegisterRequest):
    """
    注册接口
    
    Args:
        request: 注册请求，包含用户名、密码和确认密码
        
    Returns:
        注册成功返回 success=True
        
    Raises:
        HTTPException:
            - 400: 密码不一致、用户名长度不合法、密码长度不合法、用户名已存在
    """
    # 验证密码是否一致
    if request.password != request.confirm_password:
        raise HTTPException(status_code=400, detail="两次输入的密码不一致")
    
    # 验证用户名长度（3-20 字符）
    if len(request.username) < 3:
        raise HTTPException(status_code=400, detail="用户名至少 3 个字符")
    
    if len(request.username) > 20:
        raise HTTPException(status_code=400, detail="用户名最多 20 个字符")
    
    # 验证密码长度（至少 6 字符）
    if len(request.password) < 6:
        raise HTTPException(status_code=400, detail="密码至少 6 个字符")
    
    # 检查用户名是否已存在
    if request.username in USERS:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    # 注册新用户
    USERS[request.username] = request.password
    save_users(USERS)
    
    return {"success": True, "message": "注册成功"}


@app.post("/api/chat")
def chat(request: ChatRequest):
    """
    聊天接口
    
    Args:
        request: 聊天请求，包含用户消息
        
    Returns:
        返回 AI 回复
    """
    # TODO: 后续接入 RAG 和 LLM
    # 目前先返回假数据
    return {"reply": f"收到你的问题：{request.message}"}
