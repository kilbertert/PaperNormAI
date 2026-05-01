PaperNormAI 论文格式校准工具 - 实现计划

▎ For agentic workers: REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

Goal: 构建一个专为学生打造的 AI 论文格式校准工具，自动检测并修正毕业论文、课程论文的排版规范，支持 Web SaaS、桌面应用和 Word 插件三种交付形态。

Architecture:
- 后端：Python FastAPI 提供 RESTful API，处理文档解析、格式检测和修正
- 前端：React + TypeScript 构建 Web 界面，Electron 打包桌面应用
- AI 引擎：混合方案 - 规则引擎处理确定性规范（字体、行距、页边距），大模型 API 处理语义类检测（参考文献格式、引用一致性）
- 文档处理：python-docx 解析 Word 文档，自研规则引擎进行格式校验
- Word 插件：Office Add-in (JavaScript) 调用后端 API

Tech Stack:
- Backend: Python 3.11+, FastAPI, python-docx, Pydantic, SQLAlchemy, PostgreSQL
- Frontend: React 18, TypeScript, Vite, TailwindCSS, Ant Design
- Desktop: Electron
- Word Add-in: Office.js, React
- AI: OpenAI API / Claude API / 国产大模型 API
- DevOps: Docker, GitHub Actions, AWS/Aliyun

---
前置阅读：`docs/architecture/2026-04-28-mvp-engineering-blueprint.md`

说明：本实现计划早于 MVP 工程架构蓝图形成，若本计划中的交付范围、模块边界或阶段划分与蓝图冲突，统一以蓝图为准。尤其是以下约束已变更为新的默认前提：

1. MVP 只做 Web + `.docx`，不并行首发桌面端和 Word 插件。
2. 后端以模块化单体为主，不以微服务为目标设计。
3. 规则引擎与模板系统是第一核心，AI 为增强层。
4. 文档处理必须围绕中间文档模型组织。

项目结构设计

PaperNormAI/
├── backend/                    # Python FastAPI 后端
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI 应用入口
│   │   ├── api/               # API 路由
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── documents.py      # 文档上传/下载
│   │   │   │   ├── validation.py     # 格式校验
│   │   │   │   ├── correction.py     # 格式修正
│   │   │   │   └── templates.py      # 高校模板管理
│   │   ├── core/              # 核心配置
│   │   │   ├── __init__.py
│   │   │   ├── config.py      # 配置管理
│   │   │   ├── security.py    # 认证授权
│   │   │   └── database.py    # 数据库连接
│   │   ├── models/            # 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── document.py
│   │   │   ├── user.py
│   │   │   └── template.py
│   │   ├── schemas/           # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── document.py
│   │   │   ├── validation.py
│   │   │   └── template.py
│   │   ├── services/          # 业务逻辑
│   │   │   ├── __init__.py
│   │   │   ├── document_parser.py    # 文档解析
│   │   │   ├── rule_engine.py        # 规则引擎
│   │   │   ├── ai_service.py         # AI 服务调用
│   │   │   ├── validator.py          # 格式校验器
│   │   │   └── corrector.py          # 格式修正器
│   │   ├── rules/             # 规则定义
│   │   │   ├── __init__.py
│   │   │   ├── base.py        # 规则基类
│   │   │   ├── font_rules.py  # 字体规则
│   │   │   ├── spacing_rules.py      # 行距/段距规则
│   │   │   ├── margin_rules.py       # 页边距规则
│   │   │   ├── heading_rules.py      # 标题层级规则
│   │   │   └── reference_rules.py    # 参考文献规则
│   │   └── utils/             # 工具函数
│   │       ├── __init__.py
│   │       ├── docx_utils.py  # Word 文档工具
│   │       └── logger.py      # 日志工具
│   ├── tests/                 # 测试
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_api/
│   │   ├── test_services/
│   │   └── test_rules/
│   ├── alembic/               # 数据库迁移
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   └── Dockerfile
│
├── frontend/                   # React 前端
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── api/               # API 调用
│   │   │   ├── client.ts
│   │   │   ├── documents.ts
│   │   │   └── validation.ts
│   │   ├── components/        # 组件
│   │   │   ├── common/
│   │   │   ├── DocumentUpload/
│   │   │   ├── ValidationReport/
│   │   │   ├── CorrectionPreview/
│   │   │   └── TemplateSelector/
│   │   ├── pages/             # 页面
│   │   │   ├── Home/
│   │   │   ├── Validation/
│   │   │   └── History/
│   │   ├── hooks/             # 自定义 hooks
│   │   ├── store/             # 状态管理 (Zustand)
│   │   ├── types/             # TypeScript 类型
│   │   └── utils/             # 工具函数
│   ├── public/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── tailwind.config.js
│
├── desktop/                    # Electron 桌面应用
│   ├── src/
│   │   ├── main/              # 主进程
│   │   │   ├── index.ts
│   │   │   └── ipc.ts
│   │   └── preload/           # 预加载脚本
│   │       └── index.ts
│   ├── package.json
│   └── electron-builder.yml
│
├── word-addin/                 # Word 插件
│   ├── src/
│   │   ├── taskpane/
│   │   │   ├── taskpane.html
│   │   │   ├── taskpane.tsx
│   │   │   └── components/
│   │   └── commands/
│   │       └── commands.ts
│   ├── manifest.xml
│   ├── package.json
│   └── webpack.config.js
│
├── shared/                     # 共享代码
│   └── types/                 # 共享类型定义
│
├── docs/                       # 文档
│   ├── api/                   # API 文档
│   ├── architecture/          # 架构文档
│   ├── rules/                 # 规则文档
│   └── superpowers/
│       └── plans/
│           └── 2026-04-28-paper-norm-ai.md
│
├── docker-compose.yml
├── .github/
│   └── workflows/
│       ├── backend-ci.yml
│       └── frontend-ci.yml
└── README.md

---

Phase 1: 项目基础设施搭建

Task 1: 初始化后端项目结构

Files:
- Create: backend/app/__init__.py
- Create: backend/app/main.py
- Create: backend/app/core/config.py
- Create: backend/requirements.txt
- Create: backend/requirements-dev.txt
- Create: backend/.env.example
- Create: backend/Dockerfile
- Step 1: 创建后端目录结构

mkdir -p backend/app/{api/v1,core,models,schemas,services,rules,utils}
mkdir -p backend/tests/{test_api,test_services,test_rules}
mkdir -p backend/alembic

- Step 2: 编写 FastAPI 应用入口

Create backend/app/main.py:

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import documents, validation, correction, templates

app = FastAPI(
    title="PaperNormAI API",
    description="AI-powered paper format validation and correction API",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(documents.router, prefix="/api/v1/documents", tags=["documents"])
app.include_router(validation.router, prefix="/api/v1/validation", tags=["validation"])
app.include_router(correction.router, prefix="/api/v1/correction", tags=["correction"])
app.include_router(templates.router, prefix="/api/v1/templates", tags=["templates"])

@app.get("/")
async def root():
    return {"message": "PaperNormAI API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

- Step 3: 编写配置管理

Create backend/app/core/config.py:

from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # App
    APP_NAME: str = "PaperNormAI"
    DEBUG: bool = False

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/papernorm"

    # AI Service
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4"

    # File Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "./uploads"

    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

- Step 4: 编写依赖文件

Create backend/requirements.txt:

fastapi==0.109.0
uvicorn[standard]==0.27.0
python-docx==1.1.0
pydantic==2.5.3
pydantic-settings==2.1.0
sqlalchemy==2.0.25
alembic==1.13.1
psycopg2-binary==2.9.9
python-multipart==0.0.6
openai==1.10.0
anthropic==0.18.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0

Create backend/requirements-dev.txt:

-r requirements.txt
pytest==7.4.4
pytest-asyncio==0.23.3
pytest-cov==4.1.0
httpx==0.26.0
black==24.1.1
flake8==7.0.0
mypy==1.8.0

- Step 5: 创建环境变量示例文件

Create backend/.env.example:

# App
APP_NAME=PaperNormAI
DEBUG=True

# CORS
ALLOWED_ORIGINS=["http://localhost:5173","http://localhost:3000"]

# Database
DATABASE_URL=postgresql://papernorm:papernorm@localhost:5432/papernorm

# AI Service
OPENAI_API_KEY=sk-xxx
OPENAI_MODEL=gpt-4

# File Upload
MAX_UPLOAD_SIZE=10485760
UPLOAD_DIR=./uploads

# Security
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

- Step 6: 编写 Dockerfile

Create backend/Dockerfile:

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p /app/uploads

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

- Step 7: 测试后端启动

cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env
uvicorn app.main:app --reload

Expected: Server starts at http://localhost:8000, visit http://localhost:8000/docs to see API documentation

- Step 8: 提交代码

git add backend/
git commit -m "feat(backend): initialize FastAPI project structure"

---
Task 2: 初始化前端项目结构

Files:
- Create: frontend/package.json
- Create: frontend/vite.config.ts
- Create: frontend/tsconfig.json
- Create: frontend/tailwind.config.js
- Create: frontend/src/main.tsx
- Create: frontend/src/App.tsx
- Create: frontend/src/api/client.ts
- Step 1: 创建 React + Vite 项目

npm create vite@latest frontend -- --template react-ts
cd frontend
npm install

- Step 2: 安装依赖

npm install axios zustand react-router-dom antd
npm install -D tailwindcss postcss autoprefixer @types/node
npx tailwindcss init -p

- Step 3: 配置 Tailwind CSS

Modify frontend/tailwind.config.js:

/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
  corePlugins: {
    preflight: false, // Disable Tailwind's base styles to avoid conflicts with Ant Design
  },
}

- Step 4: 配置 Vite

Modify frontend/vite.config.ts:

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})

- Step 5: 配置 TypeScript

Modify frontend/tsconfig.json:

{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}

- Step 6: 创建 API 客户端

Create frontend/src/api/client.ts:

import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;

- Step 7: 创建基础 App 组件

Modify frontend/src/App.tsx:

import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import './App.css';

function App() {
  return (
    <ConfigProvider locale={zhCN}>
      <div className="min-h-screen bg-gray-50">
        <header className="bg-white shadow">
          <div className="max-w-7xl mx-auto py-6 px-4">
            <h1 className="text-3xl font-bold text-gray-900">
              PaperNormAI - 论文格式校准工具
            </h1>
          </div>
        </header>
        <main className="max-w-7xl mx-auto py-6 px-4">
          <p className="text-gray-600">
            专为学生打造的 AI 论文格式校准工具
          </p>
        </main>
      </div>
    </ConfigProvider>
  );
}

export default App;

- Step 8: 创建环境变量文件

Create frontend/.env.development:

VITE_API_BASE_URL=http://localhost:8000/api/v1

Create frontend/.env.production:

VITE_API_BASE_URL=/api/v1

- Step 9: 测试前端启动

cd frontend
npm run dev

Expected: Dev server starts at http://localhost:5173

- Step 10: 提交代码

git add frontend/
git commit -m "feat(frontend): initialize React + Vite project structure"

---
Task 3: 设置数据库和 Docker 环境

Files:
- Create: docker-compose.yml
- Create: backend/app/core/database.py
- Create: backend/app/models/__init__.py
- Create: backend/alembic.ini
- Create: backend/alembic/env.py
- Step 1: 创建 Docker Compose 配置

Create docker-compose.yml:

version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: papernorm-postgres
    environment:
      POSTGRES_USER: papernorm
      POSTGRES_PASSWORD: papernorm
      POSTGRES_DB: papernorm
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U papernorm"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: papernorm-backend
    environment:
      DATABASE_URL: postgresql://papernorm:papernorm@postgres:5432/papernorm
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
      - backend_uploads:/app/uploads
    depends_on:
      postgres:
        condition: service_healthy
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: papernorm-frontend
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      VITE_API_BASE_URL: http://localhost:8000/api/v1
    command: npm run dev -- --host

volumes:
  postgres_data:
  backend_uploads:

- Step 2: 创建前端 Dockerfile

Create frontend/Dockerfile:

FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host"]

- Step 3: 配置数据库连接

Create backend/app/core/database.py:

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

- Step 4: 初始化 Alembic

cd backend
alembic init alembic

- Step 5: 配置 Alembic

Modify backend/alembic.ini:

[alembic]
script_location = alembic
prepend_sys_path = .
sqlalchemy.url = postgresql://papernorm:papernorm@localhost:5432/papernorm

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S

Modify backend/alembic/env.py:

from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.config import settings
from app.core.database import Base
from app.models import *  # Import all models

config = context.config

# Override sqlalchemy.url with settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

- Step 6: 测试 Docker 环境

docker-compose up -d postgres
docker-compose ps

Expected: PostgreSQL container is running and healthy

- Step 7: 测试数据库连接

cd backend
python -c "from app.core.database import engine; print(engine.connect())"

Expected: Connection successful

- Step 8: 提交代码

git add docker-compose.yml backend/app/core/database.py backend/alembic.ini backend/alembic/ frontend/Dockerfile
git commit -m "feat(infra): setup Docker and database configuration"

---

---
Phase 2: 核心文档处理模块

Task 4: 实现 Word 文档解析器

Files:
- Create: backend/app/services/document_parser.py
- Create: backend/app/schemas/document.py
- Create: backend/tests/test_services/test_document_parser.py
- Create: backend/tests/fixtures/sample.docx
- Step 1: 编写文档解析器测试

Create backend/tests/test_services/test_document_parser.py:

import pytest
from pathlib import Path
from app.services.document_parser import DocumentParser, ParsedDocument

@pytest.fixture
def sample_docx_path():
    return Path(__file__).parent.parent / "fixtures" / "sample.docx"

def test_parse_document_structure(sample_docx_path):
    parser = DocumentParser()
    result = parser.parse(sample_docx_path)

    assert isinstance(result, ParsedDocument)
    assert result.paragraphs is not None
    assert len(result.paragraphs) > 0
    assert result.metadata is not None

def test_extract_font_info(sample_docx_path):
    parser = DocumentParser()
    result = parser.parse(sample_docx_path)

    first_para = result.paragraphs[0]
    assert "font_name" in first_para
    assert "font_size" in first_para

def test_extract_spacing_info(sample_docx_path):
    parser = DocumentParser()
    result = parser.parse(sample_docx_path)

    first_para = result.paragraphs[0]
    assert "line_spacing" in first_para
    assert "space_before" in first_para
    assert "space_after" in first_para

- Step 2: 运行测试确认失败

cd backend
pytest tests/test_services/test_document_parser.py -v

Expected: FAIL - DocumentParser not defined

- Step 3: 定义文档数据结构

Create backend/app/schemas/document.py:

from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class ParagraphInfo(BaseModel):
    index: int
    text: str
    style: Optional[str] = None
    font_name: Optional[str] = None
    font_size: Optional[float] = None  # in points
    font_bold: bool = False
    font_italic: bool = False
    line_spacing: Optional[float] = None
    space_before: Optional[float] = None  # in points
    space_after: Optional[float] = None  # in points
    alignment: Optional[str] = None
    first_line_indent: Optional[float] = None  # in points
    left_indent: Optional[float] = None
    right_indent: Optional[float] = None
    is_heading: bool = False
    heading_level: Optional[int] = None

class SectionInfo(BaseModel):
    index: int
    page_width: float  # in points
    page_height: float
    margin_top: float
    margin_bottom: float
    margin_left: float
    margin_right: float
    header_distance: float
    footer_distance: float

class DocumentMetadata(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    created: Optional[datetime] = None
    modified: Optional[datetime] = None
    page_count: Optional[int] = None

class ParsedDocument(BaseModel):
    metadata: DocumentMetadata
    sections: List[SectionInfo]
    paragraphs: List[ParagraphInfo]
    tables: List[Dict[str, Any]] = []
    images: List[Dict[str, Any]] = []

- Step 4: 实现文档解析器

Create backend/app/services/document_parser.py:

from pathlib import Path
from typing import Union
from docx import Document
from docx.shared import Pt
from docx.enum.text

※ recap: I'm creating a detailed implementation plan for PaperNormAI, an AI-powered paper format validation tool for students. The plan covers backend (Python FastAPI), frontend (React), desktop app (Electron), and Word plugin, with mixed rule-engine and LLM approach for format checking. I was writing the document parser implementation when you stepped away - next I'll complete that task and continue with the remaining core modules. (disable recaps in /config)
