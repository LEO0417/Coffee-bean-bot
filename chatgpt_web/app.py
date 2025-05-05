# 安装所需的包：
# pip install flask openai python-dotenv borax requests
from flask import Flask, render_template, request, jsonify, send_file
from openai import OpenAI
import os
from dotenv import load_dotenv
from datetime import datetime
import tempfile
from borax.calendars.lunardate import LunarDate
import requests
import json
import ollama

# 加载环境变量
load_dotenv()

app = Flask(__name__)

# 从环境变量中获取 API 密钥
DEFAULT_API_KEY = os.getenv("OPENAI_API_KEY")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")  # Ollama 默认地址

class ModelProvider:
    OPENAI = "openai"
    OLLAMA = "ollama"

# 支持的模型列表
SUPPORTED_MODELS = {
    ModelProvider.OPENAI: {
        "gpt-3.5-turbo": "GPT-3.5 Turbo",
        "gpt-4": "GPT-4",
        "gpt-4-turbo": "GPT-4 Turbo"
    },
    ModelProvider.OLLAMA: {}  # 将通过 API 动态获取
}

def get_ollama_models():
    """获取所有可用的 Ollama 模型"""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags")
        if response.status_code == 200:
            models = response.json().get('models', [])
            return {model['name']: model['name'].capitalize() for model in models}
        return {}
    except Exception as e:
        print(f"获取 Ollama 模型失败：{str(e)}")
        return {}

def get_current_time_info():
    now = datetime.now()
    weekdays = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
    weekday = weekdays[now.weekday()]
    
    # 获取时段描述
    hour = now.hour
    if 5 <= hour < 12:
        period = "早上"
    elif 12 <= hour < 14:
        period = "中午"
    elif 14 <= hour < 18:
        period = "下午"
    else:
        period = "晚上"
    
    # 添加农历日期
    lunar_date = LunarDate.from_solar_date(now.year, now.month, now.day)
    lunar_str = f"{lunar_date.year}年{lunar_date.month}月{lunar_date.day}日"
    
    return {
        'datetime': now.strftime('%Y年%m月%d日 %H:%M'),
        'weekday': weekday,
        'period': period,
        'lunar_date': lunar_str  # 添加农历日期
    }

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get-models', methods=['GET'])
def get_models():
    try:
        # 获取 OpenAI 模型
        client = OpenAI(
            api_key=DEFAULT_API_KEY,
            base_url="https://api.openai.com/v1"
        )
        
        openai_models = {}
        try:
            models = client.models.list()
            for model in models.data:
                model_id = model.id
                if 'gpt' in model_id.lower():
                    display_name = model_id.replace("-", " ").title()
                    openai_models[model_id] = display_name
        except Exception as e:
            print(f"获取 OpenAI 模型失败：{str(e)}")
            openai_models = SUPPORTED_MODELS[ModelProvider.OPENAI]

        # 获取 Ollama 模型
        ollama_models = get_ollama_models()
        
        # 合并所有模型
        all_models = {
            ModelProvider.OPENAI: openai_models,
            ModelProvider.OLLAMA: ollama_models
        }
        
        return jsonify(all_models)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def chat_with_ollama(message, model_name, system_prompt):
    """使用 Ollama Python 客户端进行对话"""
    try:
        # 设置 Ollama 客户端的主机
        ollama.host = OLLAMA_BASE_URL
        
        # 使用 Ollama 客户端调用模型
        response = ollama.chat(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ]
        )
        
        # 从响应中获取内容
        if "message" in response and "content" in response["message"]:
            return response["message"]["content"]
        else:
            return f"Ollama 响应格式不正确：{response}"
    except Exception as e:
        return f"调用 Ollama 失败：{str(e)}"

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        message = data.get('message')
        model = data.get('model', 'gpt-3.5-turbo')
        provider = data.get('provider', ModelProvider.OPENAI)

        if not message:
            return jsonify({'error': '消息不能为空'}), 400

        # 获取当前时间信息
        time_info = get_current_time_info()
        
        # 构建系统提示，包含时间信息
        system_prompt = f"""你是一位专业的咖啡顾问，熟悉各种咖啡豆、烘焙方法和冲泡技巧。
现在是{time_info['datetime']} {time_info['weekday']}，{time_info['period']}好。
请根据当前时间，以专业且友好的方式回答用户的问题。
如果用户询问与时间相关的问题，请基于当前时间回答。
如果是早上，可以推荐清爽提神的咖啡；
中午可以推荐提升工作效率的咖啡；
下午可以推荐享受下午茶时光的咖啡；
晚上则推荐低因的温和咖啡。

在回答用户问题时，你可以在<think>标签内分析和思考问题，这部分内容不会直接显示给用户。
你的最终回答应该放在<think>标签之外，这部分会显示给用户。
例如：
<think>这里是思考过程...</think>
这里是给用户的实际回答..."""

        if provider == ModelProvider.OLLAMA:
            # 使用 Ollama API
            response_text = chat_with_ollama(message, model, system_prompt)
            
            # 处理响应中的思考标签
            cleaned_response = remove_think_tags(response_text)
            return jsonify({'response': cleaned_response})
        else:
            # 使用 OpenAI API
            client = OpenAI(
                api_key=DEFAULT_API_KEY,
                base_url="https://api.openai.com/v1"
            )
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ]
            )
            
            # 处理响应中的思考标签
            response_text = response.choices[0].message.content
            cleaned_response = remove_think_tags(response_text)
            
            return jsonify({
                'response': cleaned_response
            })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def remove_think_tags(text):
    """移除文本中<think>标签内的内容"""
    import re
    # 使用正则表达式移除<think>标签及其内容
    cleaned_text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    return cleaned_text.strip()

@app.route('/text-to-speech', methods=['POST'])
def text_to_speech():
    try:
        data = request.json
        text = data.get('text')

        if not text:
            return jsonify({'error': '文本不能为空'}), 400

        # 创建 OpenAI 客户端
        client = OpenAI(
            api_key=DEFAULT_API_KEY,
            base_url="https://api.openai.com/v1"
        )

        # 创建临时文件来保存音频
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
            # 调用 OpenAI TTS API
            response = client.audio.speech.create(
                model="tts-1",  # 或者使用 tts-1-hd 获得更高质量
                voice="shimmer",  # 可选：alloy, echo, fable, onyx, nova, shimmer
                input=text
            )
            
            # 将音频数据保存到临时文件
            response.stream_to_file(temp_file.name)
            
            # 返回音频文件
            return send_file(
                temp_file.name,
                mimetype='audio/mpeg',
                as_attachment=True,
                download_name='speech.mp3'
            )

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001) 