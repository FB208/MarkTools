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
flask --app app run --debug

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

# 登录到Docker Hub
docker login

# 打包镜像
docker build -f docker/Dockerfile -t fb208/marktools:0.3.3 .

# 推送镜像到Docker Hub
docker push fb208/marktools:0.3.3

# 运行docker镜像
docker run -p 5000:5000 \
    -e SECRET_KEY=my_secret_key \
    -e OPENAI_API_KEY=my_openai_api_key \
    -e OPENAI_BASE_URL=https://api.deepseek.com/v1/ \
    my_flask_app

# docker-compose启动

```

# 关于google cloud
若使用google cloud的服务，需要安装google cloud sdk，神tm麻烦
## 安装
```
# windows powershell 执行
(New-Object Net.WebClient).DownloadFile("https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe", "$env:Temp\GoogleCloudSDKInstaller.exe")

& $env:Temp\GoogleCloudSDKInstaller.exe
```
安装完多一个Cloud Tools for PowerShell

## 获取身份验证文件
1. 登录Google Cloud Console (https://console.cloud.google.com/)
2. 选择您的项目
3. 在左侧菜单中，导航到"IAM & Admin" > "Service Accounts"
4. 如果您还没有服务账号，点击页面顶部的"CREATE SERVICE ACCOUNT"创建一个新的服务账号。如果已有服务账号，跳到第7步。
5. 填写服务账号详情（名称、描述等）
6. 为服务账号分配适当的角色（例如，对于Cloud Storage，可能需要"Storage Object Viewer"或"Storage Object Creator"等角色）
7. 在服务账号列表中，找到您想使用的服务账号
8. 点击该服务账号的电子邮件地址，进入服务账号详情页面
9. 在"Keys"标签页下，点击"ADD KEY" > "Create new key"
10. 选择"JSON"作为密钥类型，然后点击"CREATE"
11. 浏览器将自动下载JSON密钥文件。请将此文件保存在安全的位置，因为它包含了访问您Google Cloud资源的凭证。
12. 将下载的文件重命名为更易识别的名称（例如my-project-credentials.json），并记住其保存位置
13. 获取文件后，您可以在代码中使用这个文件路径：
```
key_path = "path/to/your/my-project-credentials.json"
credentials = service_account.Credentials.from_service_account_file(key_path)
```
14. 环境变量设置方法
```
  set GOOGLE_APPLICATION_CREDENTIALS=path\to\your\my-project-credentials.json
```
## 使用
```
# 初始化
gcloud init

```