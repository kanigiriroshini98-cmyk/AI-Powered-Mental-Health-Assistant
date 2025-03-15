from flask import Flask, request, jsonify, render_template, send_from_directory
import openai
from dotenv import load_dotenv
import os
from datetime import datetime

# بارگذاری کلید API از فایل .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# مقداردهی از متغیرهای محیطی
APP_NAME = os.getenv("FLASK_APP_NAME", "Mental Health Assistant")
APP_ENV = os.getenv("FLASK_ENV", "development")
PORT = int(os.getenv("FLASK_PORT", 5005))
APPLICATION_ROOT = os.getenv("FLASK_APPLICATION_ROOT", "/assistant")
STATIC_URL_PATH = os.getenv("FLASK_STATIC_URL_PATH", "/assistant/static")

# ایجاد Flask app
app = Flask(
    __name__, 
    static_folder="static", 
    template_folder="templates", 
    static_url_path=STATIC_URL_PATH
)
app.config["APPLICATION_ROOT"] = APPLICATION_ROOT

@app.route(f"{APPLICATION_ROOT}/")
def index():
    """صفحه اصلی که رابط کاربری را نمایش می‌دهد"""
    return render_template("index.html", APPLICATION_ROOT=APPLICATION_ROOT)

@app.route(f"{APPLICATION_ROOT}/analyze", methods=["POST"])
def analyze():
    """آنالیز ورودی کاربر و ارائه پاسخ مناسب"""
    user_input = request.json.get("text")
    user_name = request.json.get("name", "User")
    user_age = request.json.get("age", "unknown")
    if not user_input:
        return jsonify({"error": "No input provided"}), 400

    # بررسی شرایط بحرانی (مانند افکار خودکشی یا آسیب)
    critical_conditions = ["suicide", "kill myself", "self-harm", "hurt myself", "end my life"]
    if any(condition in user_input.lower() for condition in critical_conditions):
        # ثبت زمان و نوع پیام اضطراری
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        emergency_message = f"Emergency Alert: A user is experiencing a critical condition. User input: '{user_input}' at {timestamp}."
        # اینجا می‌توانید منطق ارسال پیام اضطراری واقعی را اضافه کنید
        print(emergency_message)
        return jsonify({
            "response": f"{user_name}, I'm really sorry that you're feeling this way. Please remember that you are not alone, and there are people who can help you. I strongly encourage you to reach out to a trusted person or contact a local mental health professional or helpline. You can also call emergency services (998) or the police (999) for immediate assistance.",
            "critical": True
        })

    try:
        # ارسال درخواست به مدل OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a highly empathetic and evidence-based mental health assistant. Your role is to understand the user's emotions deeply, validate their feelings, and provide actionable, practical, and specific solutions to help them feel better. Consider the user's name and age to personalize the response. Offer step-by-step guidance, coping techniques, and suggestions for lifestyle changes that can improve their mental health. Be as clear and supportive as possible, giving the user tangible actions they can take right now."},
                {"role": "user", "content": f"Name: {user_name}, Age: {user_age}. {user_input}"}
            ]
        )
        assistant_response = response['choices'][0]['message']['content'].strip()
        return jsonify({"response": assistant_response, "user_input": user_input, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})

    except Exception as e:
        print("Error occurred:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route(f"{APPLICATION_ROOT}/static/<path:filename>")
def static_files(filename):
    return send_from_directory(app.static_folder, filename)

if __name__ == "__main__":
    print(f"Starting {APP_NAME} in {APP_ENV} mode on port {PORT}...")
    app.run(host="0.0.0.0", port=PORT, debug=(APP_ENV == "development"))
