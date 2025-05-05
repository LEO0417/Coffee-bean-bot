# 安装所需的包：
# pip install flask openai python-dotenv borax
from flask import Flask, render_template, request, jsonify, send_file
from openai import OpenAI
import os
from dotenv import load_dotenv
from datetime import datetime
import tempfile
from borax.calendars.lunardate import LunarDate

# 加载环境变量
load_dotenv()

app = Flask(__name__)

# 支持的模型列表
SUPPORTED_MODELS = {
    "gpt-3.5-turbo": "GPT-3.5 Turbo",
    "gpt-4": "GPT-4",
    "gpt-4-turbo": "GPT-4 Turbo"
}
# 从环境变量中获取 API 密钥
DEFAULT_API_KEY = os.getenv("OPENAI_API_KEY")

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
        # 创建 OpenAI 客户端
        client = OpenAI(
            api_key=DEFAULT_API_KEY,
            base_url="https://api.openai.com/v1"
        )
        
        # 获取模型列表
        models = client.models.list()
        
        # 只保留 GPT-4.1 和 GPT-4o 的对话模型
        gpt_models = {}
        
        # 筛选 GPT-4.1 和 GPT-4o 的最新版本
        gpt41_models = []
        gpt4o_models = []
        
        for model in models.data:
            model_id = model.id
            # 只保留对话模型（不包含 vision, embedding, instruct 等特殊用途模型）
            if ('gpt-4.1' in model_id.lower() and not any(x in model_id.lower() for x in ['vision', 'embedding'])):
                gpt41_models.append(model_id)
            elif ('gpt-4o' in model_id.lower() and not any(x in model_id.lower() for x in ['vision', 'embedding'])):
                gpt4o_models.append(model_id)
        
        # 添加 GPT-4.1 的最新版本（如果有）
        if gpt41_models:
            latest_gpt41 = sorted(gpt41_models)[-1]  # 获取按字母顺序排序的最后一个（通常是最新版本）
            gpt_models[latest_gpt41] = "GPT-4.1"
        
        # 添加 GPT-4o 的最新版本（如果有）
        if gpt4o_models:
            latest_gpt4o = sorted(gpt4o_models)[-1]  # 获取按字母顺序排序的最后一个（通常是最新版本）
            gpt_models[latest_gpt4o] = "GPT-4o"
        
        # 添加默认模型（以防找不到 GPT-4.1 和 GPT-4o）
        if not gpt_models:
            gpt_models["gpt-3.5-turbo"] = "GPT-3.5 Turbo"
        
        return jsonify(gpt_models)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        message = data.get('message')
        model = data.get('model', 'gpt-3.5-turbo')

        if not message:
            return jsonify({'error': '消息不能为空'}), 400

        # 获取当前时间信息
        time_info = get_current_time_info()
        
        # 创建 OpenAI 客户端
        client = OpenAI(
            api_key=DEFAULT_API_KEY,
            base_url="https://api.openai.com/v1"
        )
        
        # 构建系统提示，包含时间信息
        system_prompt = f"""你是一位专业的咖啡顾问，熟悉各种咖啡豆、烘焙方法和冲泡技巧。
现在是{time_info['datetime']} {time_info['weekday']}，{time_info['period']}好。
请根据当前时间，以专业且友好的方式回答用户的问题。
如果用户询问与时间相关的问题，请基于当前时间回答。
如果是早上，可以推荐清爽提神的咖啡；
中午可以推荐提升工作效率的咖啡；
下午可以推荐享受下午茶时光的咖啡；
晚上则推荐低因的温和咖啡。"""
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ]
        )

        return jsonify({
            'response': response.choices[0].message.content
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

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