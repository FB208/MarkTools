from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/translate')
def translate_page():
    return render_template('translate.html')

@app.route('/translate_api', methods=['POST'])
def translate():
    data = request.get_json()
    chinese_text = data.get('chinese', '')
    english_text = data.get('english', '')
    direction = data.get('direction', '')

    if direction == 'zh_to_en':
        # 这里添加中文翻译为英文的逻辑
        translation = f"Translated to English: {chinese_text}"
    elif direction == 'en_to_zh':
        # 这里添加英文翻译为中文的逻辑
        translation = f"翻译成中文: {english_text}"
    else:
        translation = ''

    return jsonify({'translation': translation})

if __name__ == '__main__':
    app.run(debug=True)