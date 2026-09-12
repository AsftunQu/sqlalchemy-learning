# SQLalchemy Learning API

基于 FastAPI + SQLAlchemy 2.0 的任务管理API，包含JWT认证、PostgreSQL

## 技术栈

- **Web 框架** : FastAPI
- **ORM** : SQLAlchemy 2.0 + Alembic 迁移
- **数据库** : PostgreSQl、Redis
- **认证** ： JWT(python-jose) + bcrypt 密码加密

## 快速开始

### 一：Docker（推荐）

```bash
cp .env.example .env   # 填入真实配置
docker compose up -d --build

```

启动后访问http://localhost:8000，接口文档在http://localhost:8000/docs

### 二：本地运行

python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env          # 填入真实配置
alembic upgrade head
uvicorn app.main:app --reload

## 环境变量

复制.env.example为.env并填写变量：
- DB_USER / DB_PASSWORD / DB_NAME = 你的PostgreSQL账号
- DB_HOST / DB_POST = 数据库地址（本地为localhost，容器内自动用postgres）
- SECRET_KEY = JWT签名密钥，终端使用python -c "import secrets; print(secrets.token_hex(32))"可生成

## 接口列表

| 方法 | 路径 | 说明 | 鉴权 |
|:---:|:---:|:---:|:---|
| `GET` | /health | 健康检查 | 否 |
| `POST` | /api/register | 用户注册 | 否 |
| `POST` | /api/login | 登录，返回JWT | 否 |
| `GET` | /api/me | 当前用户信息 | 是 |
| `POST` | /api/tasks | 创建任务 | 是 |
| `GET` | /api/tasks | 任务列表（分页/筛选） | 是 |
| `GET` | /api/tasks/{id} | 任务详情 | 是 |
| `PATCH` | /api/tasks/{id} | 更新任务 | 是 |
| `DELETE` | /api/tasks/{id} | 删除任务（软删除） | 是 |

## 项目结构

.
├── app/                 # 应用代码(models / schemas / services / utils)
├── alembic/             # 数据库迁移
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
