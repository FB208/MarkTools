# MarkTools

## 创建虚拟环境
```
python -m venv marktools.venv

marktools.venv\Scripts\activate
```

## 安装依赖
```
pip install -r requirements.txt
```

## 启动项目

```
# 普通启动
flask --app app run
# 调试模式
flask --app run run --debug
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