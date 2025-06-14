# Python项目开发规则

## 环境要求
- 操作系统：Ubuntu 20.04
- Python版本管理：使用uv创建和管理虚拟环境
- 权限：无sudo权限
- Python命令：使用`python`而不是`python3`

## 项目结构规范

```
project_root/
├── .python-version          # Python版本文件
├── pyproject.toml           # 项目配置和依赖管理
├── uv.lock                  # 依赖锁定文件
├── .gitignore              # Git忽略文件
├── README.md               # 项目说明文档
├── app.py                  # 主应用入口
├── config.py               # 配置文件
├── start_server.py         # 服务启动脚本
├── models/                 # 数据模型
│   ├── __init__.py
│   └── *.py
├── routes/                 # 路由处理
│   ├── __init__.py
│   └── *.py
├── services/               # 业务逻辑服务
│   ├── __init__.py
│   └── *.py
├── utils/                  # 工具函数
│   ├── __init__.py
│   └── *.py
├── scripts/                # 脚本文件
│   └── *.py
├── templates/              # 模板文件（如果是Web项目）
│   └── *.html
├── static/                 # 静态资源（如果是Web项目）
│   ├── css/
│   ├── js/
│   └── images/
├── database/               # 数据库文件
│   └── *.db
├── tests/                  # 测试文件
│   ├── __init__.py
│   └── test_*.py
└── docs/                   # 文档
    └── *.md
```

## 虚拟环境管理

### 创建虚拟环境
```bash
# 在项目根目录下
uv venv
```

### 激活虚拟环境
```bash
source .venv/bin/activate
```

### 退出虚拟环境
```bash
deactivate
```

### 安装依赖
```bash
# 安装项目依赖
uv pip install -r requirements.txt
# 或者使用pyproject.toml
uv pip install -e .
```

### 添加新依赖
```bash
# 添加运行时依赖
uv add package_name
# 添加开发依赖
uv add --dev package_name
```

## 代码规范

### 1. 文件命名
- 使用小写字母和下划线
- 模块名应该简短且有意义
- 避免使用Python关键字

### 2. 函数和类命名
- 函数名：使用小写字母和下划线（snake_case）
- 类名：使用驼峰命名法（PascalCase）
- 常量：使用大写字母和下划线

### 3. 注释规范
- 每个函数必须有docstring说明
- 复杂逻辑需要添加行内注释
- 使用中文注释说明业务逻辑

```python
def process_audio_data(audio_file_path: str) -> dict:
    """
    处理音频数据并返回处理结果
    
    Args:
        audio_file_path (str): 音频文件路径
        
    Returns:
        dict: 包含处理结果的字典
        
    Raises:
        FileNotFoundError: 当音频文件不存在时抛出
    """
    # 检查文件是否存在
    if not os.path.exists(audio_file_path):
        raise FileNotFoundError(f"音频文件不存在: {audio_file_path}")
    
    # 处理音频数据的具体逻辑
    result = {}
    return result
```

### 4. 导入规范
- 标准库导入放在最前面
- 第三方库导入放在中间
- 本地模块导入放在最后
- 每组导入之间用空行分隔

```python
# 标准库
import os
import sys
from typing import Dict, List

# 第三方库
from flask import Flask, request
import numpy as np

# 本地模块
from models.user_model import User
from services.audio_service import AudioService
```

## 开发流程

### 1. 启动开发环境
```bash
# 激活虚拟环境
source .venv/bin/activate

# 启动应用
python start_server.py

```

### 2. 数据库管理
```bash
# 初始化数据库
python scripts/init_db.py

# 管理数据库
python scripts/manage_db.py
```

### 3. 测试
```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试文件
python -m pytest tests/test_specific.py

# 运行API测试
python test_api.py
```

## 配置管理

### 1. 环境配置
- 使用`config.py`管理配置
- 敏感信息使用环境变量
- 不同环境使用不同配置文件

### 2. 数据库配置
- 开发环境使用SQLite
- 数据库文件放在`database/`目录下
- 定期备份重要数据

## Git规范

### 1. .gitignore配置
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# 虚拟环境
.venv/
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# 数据库
*.db
*.sqlite3

# 日志
*.log

# 临时文件
.tmp/
temp/
```

### 2. 提交规范
- 提交信息使用中文
- 格式：`类型: 简短描述`
- 类型包括：功能、修复、重构、文档、测试等

```
功能: 添加用户登录功能
修复: 解决音频播放器的暂停问题
重构: 优化数据库查询性能
文档: 更新API文档
测试: 添加用户服务单元测试
```

## 部署规范

### 1. 生产环境准备
```bash
# 安装生产依赖
uv pip install --no-dev

# 设置环境变量
export FLASK_ENV=production
export DATABASE_URL=production_db_url
```

### 2. 性能优化
- 使用生产级WSGI服务器（如Gunicorn）
- 配置适当的日志级别
- 优化数据库查询
- 启用缓存机制

## 安全规范

### 1. 代码安全
- 不在代码中硬编码敏感信息
- 使用环境变量管理密钥
- 定期更新依赖包

### 2. 数据安全
- 用户密码必须加密存储
- 实施适当的访问控制
- 定期备份重要数据

## 故障排查

### 1. 常见问题
- 虚拟环境激活失败：检查uv安装和路径
- 依赖安装失败：检查网络连接和包名
- 数据库连接失败：检查数据库文件权限

### 2. 调试工具
- 使用`python debug_db.py`调试数据库
- 查看应用日志定位问题
- 使用断点调试复杂逻辑

## 文档维护

### 1. 代码文档
- 保持README.md更新
- 维护API文档
- 记录重要的设计决策

### 2. 变更记录
- 记录重要功能变更
- 维护版本发布说明
- 更新部署文档

---

**注意事项：**
- 每次新开一个终端时，都要先激活虚拟环境
- 始终在虚拟环境中开发
- 定期更新依赖包
- 遵循代码规范和注释要求
- 及时提交代码变更
- 保持项目结构整洁
