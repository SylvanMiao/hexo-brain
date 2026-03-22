"""
博客文章处理模块

功能：
- 读取 Hexo 博客文章
- 解析 Markdown 文件
- 文本切块
"""

import os
import re
import json
import markdown
from typing import List, Dict
from dataclasses import dataclass


@dataclass
class BlogPost:
    """博客文章数据结构"""
    title: str
    content: str  # 纯文本内容
    html: str     # HTML 格式（可选）
    filepath: str
    metadata: Dict  # Front-matter 元数据


def extract_front_matter(content: str) -> tuple[str, Dict]:
    """
    提取 Markdown 的 Front-matter 元数据
    
    Hexo 使用 YAML 格式的 Front-matter，例如：
    ---
    title: 文章标题
    date: 2024-01-01
    tags: [Python, AI]
    ---
    
    Args:
        content: Markdown 文件完整内容
        
    Returns:
        (正文内容，元数据字典)
    """
    metadata = {}
    
    # 匹配 Front-matter 块
    pattern = r'^---\s*\n(.*?)\n---\s*\n'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        front_matter = match.group(1)
        content = content[match.end():]  # 移除 Front-matter
        
        # 简单解析 YAML（仅处理常用字段）
        for line in front_matter.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                # 处理数组格式，如 [Python, AI]
                if value.startswith('[') and value.endswith(']'):
                    value = [v.strip() for v in value[1:-1].split(',')]
                metadata[key] = value
    
    return content, metadata


def markdown_to_text(html: str) -> str:
    """
    将 HTML 转换为纯文本
    
    保留代码块内容，移除其他 HTML 标签
    """
    # 提取代码块内容，转为文字格式
    def replace_pre(match):
        code = match.group(1)
        return f"\n代码：{code}\n"
    
    text = re.sub(r'<pre[^>]*><code[^>]*>(.*?)</code></pre>', replace_pre, html, flags=re.DOTALL)
    
    # 处理单独的 <code> 标签
    text = re.sub(r'<code[^>]*>(.*?)</code>', r' `\1` ', text, flags=re.DOTALL)
    
    # 移除其他 HTML 标签
    text = re.sub(r'<[^>]+>', '', text)
    
    # 解码 HTML 实体
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&amp;', '&')
    
    # 清理空白
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def parse_markdown_file(filepath: str) -> BlogPost:
    """
    解析单个 Markdown 文件
    
    Args:
        filepath: Markdown 文件路径
        
    Returns:
        BlogPost 对象
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取 Front-matter
    md_content, metadata = extract_front_matter(content)
    
    # 转换为 HTML
    html = markdown.markdown(md_content, extensions=['extra', 'codehilite'])
    
    # 转换为纯文本
    text = markdown_to_text(html)
    
    # 从文件名或元数据获取标题
    title = metadata.get('title', os.path.basename(filepath).replace('.md', ''))
    
    return BlogPost(
        title=title,
        content=text,
        html=html,
        filepath=filepath,
        metadata=metadata
    )


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    将文本切分成块
    
    Args:
        text: 要切分的文本
        chunk_size: 每块最大字符数
        overlap: 块之间重叠的字符数
        
    Returns:
        文本块列表
    """
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        
        # 尝试在句子边界处切分
        if end < len(text):
            # 查找最后一个句号、问号等
            last_punct = max(
                chunk.rfind('。'),
                chunk.rfind('！'),
                chunk.rfind('？'),
                chunk.rfind('！'),
                chunk.rfind('.')
            )
            if last_punct > chunk_size // 2:
                chunk = chunk[:last_punct + 1]
                end = start + last_punct + 1
        
        chunks.append(chunk.strip())
        start = end - overlap
    
    return chunks


def process_blog_post(post: BlogPost, chunk_size: int = 500, overlap: int = 50) -> List[Dict]:
    """
    处理博客文章，生成带元数据的文本块
    
    Args:
        post: BlogPost 对象
        chunk_size: 每块最大字符数
        overlap: 块之间重叠的字符数
        
    Returns:
        文本块列表，每个块包含内容和元数据
    """
    chunks = chunk_text(post.content, chunk_size, overlap)
    
    result = []
    for i, chunk in enumerate(chunks):
        result.append({
            'title': post.title,
            'content': chunk,
            'chunk_index': i,
            'total_chunks': len(chunks),
            'filepath': post.filepath,
            'metadata': post.metadata
        })
    
    return result


def load_hexo_posts(posts_dir: str) -> List[BlogPost]:
    """
    加载 Hexo 博客目录下的所有文章
    
    Args:
        posts_dir: Hexo 的 _posts 目录路径
        
    Returns:
        BlogPost 对象列表
    """
    posts = []
    
    if not os.path.exists(posts_dir):
        print(f"警告：目录不存在 - {posts_dir}")
        return posts
    
    # 遍历目录查找 .md 文件
    for filename in os.listdir(posts_dir):
        if filename.endswith('.md'):
            filepath = os.path.join(posts_dir, filename)
            try:
                post = parse_markdown_file(filepath)
                posts.append(post)
                print(f"已加载：{post.title}")
            except Exception as e:
                print(f"加载失败 {filename}: {e}")
    
    return posts


def process_all_posts(posts_dir: str, chunk_size: int = 500, overlap: int = 50) -> List[Dict]:
    """
    批量处理所有博客文章
    
    Args:
        posts_dir: Hexo 的 _posts 目录路径
        chunk_size: 每块最大字符数
        overlap: 块之间重叠的字符数
        
    Returns:
        所有文本块列表
    """
    posts = load_hexo_posts(posts_dir)
    
    all_chunks = []
    for post in posts:
        chunks = process_blog_post(post, chunk_size, overlap)
        all_chunks.extend(chunks)
    
    print(f"\n共处理 {len(posts)} 篇文章，生成 {len(all_chunks)} 个文本块")
    return all_chunks


def save_chunks_to_json(chunks: List[Dict], output_file: str):
    """
    将文本块保存到 JSON 文件
    
    Args:
        chunks: 文本块列表
        output_file: 输出文件路径
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    print(f"已保存到：{output_file}")


def load_chunks_from_json(input_file: str) -> List[Dict]:
    """
    从 JSON 文件加载文本块
    
    Args:
        input_file: 输入文件路径
        
    Returns:
        文本块列表
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        return json.load(f)


if __name__ == "__main__":
    # 测试代码
    print("博客文章处理模块 - 测试")
    print("=" * 50)
    
    # 示例：解析当前目录下的测试文件
    test_dir = "./test_posts"
    output_file = "./embeddings.json"
    
    if os.path.exists(test_dir):
        all_chunks = process_all_posts(test_dir, chunk_size=300, overlap=30)
        
        # 保存到 JSON
        save_chunks_to_json(all_chunks, output_file)
        
        print("\n前 3 个文本块预览：")
        for i, chunk in enumerate(all_chunks[:3]):
            print(f"\n--- 块 {i+1} ---")
            print(f"标题：{chunk['title']}")
            print(f"内容：{chunk['content'][:100]}...")
    else:
        print(f"测试目录不存在：{test_dir}")
        print("请创建测试目录并放入一些 Markdown 文件")
