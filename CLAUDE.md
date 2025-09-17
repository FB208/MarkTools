# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup
```bash
# 创建Python虚拟环境
python -m venv marktools.venv
marktools.venv\Scripts\activate

# 或使用conda
conda create --name marktools python=3.10.11
conda activate marktools

# 安装Python依赖
pip install -r requirements.txt

# 安装并编译CSS
npm install
npm run build:css

# 实时编译CSS (开发时使用)
npm run watch:css
```

### Development Server
```bash
# 调试模式启动Flask应用
npm run dev
# 或
flask --app app.py run --debug

# 普通模式启动
flask --app app run
```

### Testing
```bash
# 运行所有测试
pytest

# 测试单个文件
pytest tests/translate_test.py

# 测试单个函数
pytest tests/translate_test.py::test_translate_text
```

### Build & Deployment
```bash
# Docker构建
docker build -f docker/Dockerfile -t docker.agnet.top/fb208/marktools:0.6.51 .

# Docker运行
docker run -p 5000:5000 \
    -e SECRET_KEY=my_secret_key \
    -e OPENAI_API_KEY=my_openai_api_key \
    -e OPENAI_BASE_URL=https://api.deepseek.com/v1/ \
    my_flask_app
```

## Architecture Overview

### Core Application Structure
- **Flask应用**: 使用Blueprint模式组织路由，主要入口在`app.py`
- **MVC架构**:
  - Models: `models/`目录，使用Peewee ORM
  - Views: `templates/`目录，Jinja2模板
  - Controllers: `routes/`目录，各功能模块的路由处理

### Key Modules
- **routes/**: 所有路由蓝图，按功能分模块（翻译、语音、文章等）
- **services/**: 业务逻辑层，各种API服务的封装
- **utils/**: 工具函数库，包含各种辅助功能
- **llm/**: 大语言模型相关功能
- **api/**: API接口层

### 主要功能模块
1. **翻译服务** (`translate.py`, `translate_service.py`)
2. **语音转文字** (`speech2text.py`, `speech2text_service.py`)
3. **文章处理** (`article.py`, `article_service.py`)
4. **微信机器人** (`wechat.py`, `starbot.py`)
5. **Word插件** (`word_plugin.py`)
6. **AI趣味功能** (`fun.py`)

### External Dependencies
- **AI服务**: 支持OpenAI、DeepSeek、智谱AI、Google Gemini等多种LLM
- **数据库**: MySQL (通过Peewee ORM)
- **缓存**: Redis, FileSystemCache
- **云服务**: Google Cloud (语音识别、存储)
- **前端**: TailwindCSS + PostCSS构建系统

### Configuration
- 环境变量配置在`config.py`中定义
- 支持多种AI服务的API密钥配置
- 通过`.env`文件管理敏感配置

### 特殊说明
- 项目包含本地embedding模型，因此体积较大
- Windows开发环境需要安装Visual C++ Build Tools来支持chromadb
- 支持Docker部署和本地开发两种模式
- 包含Word Office插件开发支持