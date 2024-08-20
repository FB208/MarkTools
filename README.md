# MarkTools

## 创建虚拟环境
```
python -m venv marktools.venv

marktools.venv\Scripts\activate
```

## 安装依赖
```
pip install -r requirements.txt
# 编译样式
## 一次性编译
npm run build:css
## 实时编译（在开发时候开启这个命令，会根据项目中的样式文件变化，实时编译styles.css文件）
npx postcss static/css/main.css -o static/css/styles.css --watch
```

## 启动项目

```
# 普通启动
flask --app app run
# 调试模式
flask --app run run --debug

# 单元测试
## 测试所有
pytest
## 测试单个文件
pytest tests/translate_test.py
## 测试单个测试函数
pytest tests/translate_test.py::test_translate_text
```

## 构建docker镜像
```
docker build -f docker/Dockerfile -t marktools .
# 登录到Docker Hub
docker login

# 为镜像打标签
docker tag marktools fb208/marktools:0.0.1

# 推送镜像到Docker Hub
docker push fb208/marktools:0.0.1

# 运行docker镜像
docker run -p 5000:5000 \
    -e SECRET_KEY=my_secret_key \
    -e OPENAI_API_KEY=my_openai_api_key \
    -e OPENAI_BASE_URL=https://api.deepseek.com/v1/ \
    my_flask_app

# docker-compose启动

```