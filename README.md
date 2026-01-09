# 智能图书管理系统

**基于Flask框架和DeepSeek AI的智能图书管理系统**

一个功能完整、易于使用的图书管理系统，集成AI智能问答功能，支持管理员和读者两种角色。

[功能特性](#功能特性) • [快速开始](#快速开始) • [技术栈](#技术栈) • [项目结构](#项目结构) • [部署指南](#部署指南)

</div>

---

## 🎯 项目简介

这是一个基于Flask框架开发的智能图书管理系统，采用MVC架构设计，支持完整的图书管理、借阅管理功能。系统集成DeepSeek AI大模型，提供智能问答服务，可根据用户借阅历史进行个性化图书推荐。

### 主要特点

- ✅ **完整的图书管理功能**：支持图书的增删改查操作
- ✅ **双角色权限管理**：区分管理员和读者角色，不同权限访问不同功能
- ✅ **智能借阅系统**：支持图书借阅、归还，自动记录借阅历史
- ✅ **AI智能问答**：集成DeepSeek API，提供智能问答服务
- ✅ **个性化推荐**：基于用户借阅历史，智能推荐相关图书
- ✅ **安全性保障**：参数化查询防止SQL注入，Session会话管理
- ✅ **优雅降级**：API不可用时自动切换到关键词匹配模式

---

## ✨ 功能特性

### 👤 用户管理模块

- **用户注册**：支持管理员和读者两种角色注册
- **用户登录**：基于Session的登录状态管理
- **权限控制**：不同角色访问不同功能模块
- **个人信息管理**：读者可查看和修改个人信息

### 📚 图书管理模块（管理员）

- **添加图书**：录入图书编号、名称、作者、出版日期、存放位置等信息
- **删除图书**：支持图书删除操作，自动检查图书状态
- **修改图书**：支持图书信息修改，验证图书编号唯一性
- **查询图书**：支持按书名搜索，显示图书详细信息

### 📖 借阅管理模块（读者）

- **图书查询**：浏览所有图书，查看借阅状态
- **借阅图书**：一键借阅，自动记录借阅信息
- **归还图书**：快速归还，自动更新图书状态
- **借阅记录**：查看历史借阅记录

### 🤖 AI智能问答模块

- **智能问答**：基于DeepSeek API的自然语言问答
- **角色区分**：针对读者和管理员提供不同的问答内容
- **上下文理解**：自动提取关键词，匹配相关图书作为上下文
- **优雅降级**：API不可用时自动切换到关键词匹配模式

### 💡 推荐系统模块

- **个性化推荐**：基于用户借阅历史分析偏好
- **智能匹配**：根据作者和关键词匹配相关图书
- **评分排序**：按匹配度排序推荐结果

### 📊 数据统计模块（管理员）

- **借阅记录查询**：查看所有借阅记录，包含借阅人信息
- **读者信息管理**：查看所有读者信息，包括借书数量统计

---

## 🛠 技术栈

### 后端技术

- **Web框架**：Flask 1.0.3
- **编程语言**：Python 3.6+
- **数据库**：MySQL 5.7+
- **数据库驱动**：PyMySQL
- **模板引擎**：Jinja2

### 前端技术

- **UI框架**：Bootstrap
- **样式**：CSS3
- **JavaScript**：原生JS

### AI服务

- **AI模型**：DeepSeek API
- **智能问答**：DeepSeek Chat API

### 架构设计

- **设计模式**：MVC（Model-View-Controller）
- **安全防护**：参数化查询、Session管理

---

## 🚀 快速开始

### 环境要求

- Python 3.6 或更高版本
- MySQL 5.7 或更高版本
- pip（Python包管理器）

### 安装步骤

#### 1. 克隆项目

```bash
git clone https://github.com/yourusername/library-management-system.git
cd library-management-system
```

#### 2. 创建虚拟环境（推荐）

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

#### 3. 安装依赖

```bash
pip install -r requirements.txt
```

#### 4. 创建数据库

在MySQL中创建数据库：

```sql
CREATE DATABASE library CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

#### 5. 初始化数据库表

执行以下SQL语句创建必要的表：

```sql
-- 用户表
CREATE TABLE IF NOT EXISTS user (
    username VARCHAR(50) PRIMARY KEY,
    psw VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'reader'
);

-- 读者信息表
CREATE TABLE IF NOT EXISTS student (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    class VARCHAR(50),
    learnnumber VARCHAR(50),
    phonenumber VARCHAR(20),
    borrownumber INT DEFAULT 0,
    username VARCHAR(50),
    FOREIGN KEY (username) REFERENCES user(username) ON DELETE CASCADE
);

-- 图书表
CREATE TABLE IF NOT EXISTS BOOK (
    number VARCHAR(50) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    author VARCHAR(100),
    publicationdate DATE,
    location VARCHAR(100) NOT NULL,
    remark VARCHAR(500),
    isborrow INT DEFAULT 0,
    borrowname VARCHAR(100),
    borrowtime DATETIME
);
```

### 配置说明

#### 1. 数据库配置

编辑 `config.py` 文件，修改数据库连接信息：

```python
class Config:
    # 数据库配置
    DB_HOST = 'localhost'      # 数据库主机
    DB_USER = 'root'           # 数据库用户名
    DB_PASSWORD = '123456'     # 数据库密码
    DB_NAME = 'library'        # 数据库名称
    DB_CHARSET = 'utf8'        # 字符集
```

#### 2. DeepSeek API配置（可选）

如果需要使用智能问答功能，需要配置DeepSeek API密钥：

**方式1：环境变量配置（推荐）**

```bash
# Windows
set DEEPSEEK_API_KEY=your-api-key-here

# Linux/macOS
export DEEPSEEK_API_KEY=your-api-key-here
```

**方式2：修改配置文件**

编辑 `config.py` 文件：

```python
class Config:
    # DeepSeek API配置
    DEEPSEEK_API_KEY = 'your-api-key-here'
    DEEPSEEK_API_URL = 'https://api.deepseek.com/v1/chat/completions'
    DEEPSEEK_MODEL = 'deepseek-chat'
```

> **注意**：如果不配置API密钥，系统会自动使用关键词匹配模式，核心功能不受影响。

#### 3. Flask配置

```python
class Config:
    SECRET_KEY = 'your-secret-key-change-this-in-production'  # Session加密密钥
    DEBUG = True  # 开发模式
```

### 运行项目

#### 开发模式

```bash
python app.py
```

访问：`http://localhost:5000`

#### 生产模式

使用Gunicorn或uWSGI部署：

```bash
# 安装Gunicorn
pip install gunicorn

# 运行
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## 📁 项目结构

```
library-management-system/
│
├── app.py                      # Flask主应用文件
├── config.py                   # 配置文件
├── mysqlUtils.py               # 数据库工具类
├── deepseek_service.py         # DeepSeek API服务封装
├── requirements.txt            # 项目依赖
├── README.md                   # 项目说明文档
│
├── models/                     # 模型层（MVC）
│   ├── __init__.py
│   ├── bookModel.py           # 图书模型
│   ├── readerModel.py         # 读者模型
│   ├── recordModel.py         # 借阅记录模型
│   └── userModel.py           # 用户模型
│
├── templates/                  # 视图层（MVC）
│   ├── login.html             # 登录页面
│   ├── register.html          # 注册页面
│   ├── addbook.html           # 添加图书页面
│   ├── deletebook.html        # 删除图书页面
│   ├── changebook.html        # 修改图书列表页面
│   ├── changebookinfor.html   # 修改图书详情页面
│   ├── querybook.html         # 查询图书页面
│   ├── borrowrecord.html      # 借阅记录页面
│   ├── readerinfor.html       # 读者信息页面
│   ├── reader_profile.html    # 读者个人信息页面
│   ├── _chat_widget.html      # 智能问答组件
│   └── 404.html               # 404错误页面
│
├── static/                     # 静态资源
│   ├── css/                   # 样式文件
│   │   ├── bootstrap.min.css
│   │   ├── common.css
│   │   └── main.css
│   └── images/                # 图片资源
│
└── docs/                       # 文档目录
    ├── 需求分析规格说明书.md
    ├── 数据库结构说明.md
    ├── API_RECHARGE_GUIDE.md
    └── CHANGELOG.md
```

---

## 🎨 功能模块

### 1. 用户认证模块

- **路由**：`/login`, `/register`
- **功能**：用户注册、登录、角色区分
- **安全**：Session管理、密码验证

### 2. 图书管理模块

- **路由**：`/addbook`, `/deletebook`, `/changebook`, `/querybook`
- **功能**：图书的增删改查
- **权限**：仅管理员可访问

### 3. 借阅管理模块

- **路由**：`/reader/querybook`, `/borrow/<bookid>`, `/return/<bookid>`
- **功能**：图书查询、借阅、归还
- **权限**：读者可访问

### 4. 推荐系统模块

- **路由**：`/recommend`
- **功能**：基于借阅历史的个性化推荐
- **算法**：作者匹配 + 关键词匹配 + 评分排序

### 5. 智能问答模块

- **路由**：`/chat`
- **功能**：AI智能问答
- **技术**：DeepSeek API + 关键词匹配降级方案

### 6. 数据统计模块

- **路由**：`/borrowrecord`, `/readerinfor`
- **功能**：借阅记录查询、读者信息管理
- **权限**：仅管理员可访问

---


---

## 🚢 部署指南

### 1. 使用Docker部署（推荐）

创建 `Dockerfile`：

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

构建和运行：

```bash
docker build -t library-management .
docker run -d -p 5000:5000 --env-file .env library-management
```

### 2. 使用Nginx + Gunicorn部署

#### 安装Nginx和Gunicorn

```bash
pip install gunicorn
sudo apt-get install nginx  # Ubuntu/Debian
```

#### 配置Gunicorn

创建 `gunicorn_config.py`：

```python
bind = "127.0.0.1:5000"
workers = 4
worker_class = "sync"
timeout = 120
```

#### 配置Nginx

编辑 `/etc/nginx/sites-available/library`：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /path/to/your/project/static;
    }
}
```

#### 启动服务

```bash
# 启动Gunicorn
gunicorn -c gunicorn_config.py app:app

# 启动Nginx
sudo systemctl start nginx
```

---

## 📖 使用说明

### 管理员功能

1. **登录系统**
   - 访问首页，选择"管理员"角色
   - 输入用户名和密码登录

2. **添加图书**
   - 点击"添加图书"菜单
   - 填写图书信息（编号、名称、作者等）
   - 点击提交

3. **管理图书**
   - 查看所有图书列表
   - 支持按书名搜索
   - 可以删除或修改图书信息

4. **查看统计数据**
   - 查看所有借阅记录
   - 查看读者信息和借书统计

### 读者功能

1. **注册账号**
   - 点击"注册"链接
   - 选择"读者"角色
   - 填写用户信息和读者信息
   - 完成注册

2. **查询和借阅图书**
   - 登录后进入图书查询页面
   - 浏览所有图书，查看借阅状态
   - 点击"借阅"按钮借阅图书
   - 点击"归还"按钮归还图书

3. **个性化推荐**
   - 点击"推荐书籍"菜单
   - 系统根据借阅历史推荐相关图书

4. **智能问答**
   - 点击页面右下角的聊天图标
   - 输入问题，获得AI智能回复

---

## ❓ 常见问题

### Q1: 如何配置DeepSeek API？

A: 有两种方式配置API密钥：
1. 设置环境变量 `DEEPSEEK_API_KEY`
2. 修改 `config.py` 文件中的 `DEEPSEEK_API_KEY`

详见 [配置说明](#配置说明)

### Q2: API不可用时系统还能使用吗？

A: 可以。系统设计了优雅降级机制，API不可用时会自动切换到关键词匹配模式，核心功能不受影响。

### Q3: 如何修改数据库连接信息？

A: 编辑 `config.py` 文件，修改 `DB_HOST`、`DB_USER`、`DB_PASSWORD` 等配置项。

### Q4: 支持哪些Python版本？

A: 支持Python 3.6及以上版本。推荐使用Python 3.8+。

### Q5: 如何重置管理员密码？

A: 直接在数据库中更新user表的psw字段，或通过注册新账号后修改数据库角色字段。

### Q6: 数据库表结构如何初始化？

A: 参考 [安装步骤](#安装步骤) 中的"初始化数据库表"部分，执行SQL语句创建表结构。



### 主要版本更新

#### v2.0 - DeepSeek智能问答集成版

- ✅ 集成DeepSeek API，提供智能问答功能
- ✅ 修复SQL注入漏洞，使用参数化查询
- ✅ 改进错误处理机制
- ✅ 增强图书管理功能验证

#### v1.0 - 基础版本

- ✅ 实现基本的图书管理功能
- ✅ 实现用户认证和权限管理
- ✅ 实现借阅管理系统
- ✅ 实现推荐系统


## 👨‍💻 作者

**项目开发者**

- GitHub: [[@yourusername](https://github.com/yourusername)](https://github.com/RM-wd)
- Email:rm_wangdong@163.com
---

## 🙏 致谢

- [Flask](https://flask.palletsprojects.com/) - 优秀的Python Web框架
- [Bootstrap](https://getbootstrap.com/) - 强大的前端框架
- [DeepSeek](https://www.deepseek.com/) - AI智能问答服务
- [MySQL](https://www.mysql.com/) - 可靠的数据库系统

---


**⭐ 如果这个项目对你有帮助，请给一个Star！⭐**



