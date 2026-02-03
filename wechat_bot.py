import requests
import os
from datetime import datetime, date

APP_ID = os.environ.get("APP_ID")
APP_SECRET = os.environ.get("APP_SECRET")
user_openids = [os.environ.get("USER_1"), os.environ.get("USER_2")]
TEMPLATE_ID = os.environ.get("TEMPLATE_ID")
DATE_TOGETHER = "2019-09-22"

HF_API_TOKEN = os.environ.get("HF_API_TOKEN")
HF_MODEL = "meta-llama/Meta-Llama-3-8B-Instruct"

def get_access_token():
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APP_ID}&secret={APP_SECRET}"
    return requests.get(url).json()["access_token"]

def date_counters():
    today = date.today()
    together = datetime.strptime(DATE_TOGETHER, "%Y-%m-%d").date()

    # Total days together
    days_since = (today - together).days

    # How many full years together
    year_count = today.year - together.year
    this_year_anniversary = together.replace(year=today.year)

    if today < this_year_anniversary:
        year_count -= 1
        next_anniversary = this_year_anniversary
    else:
        next_anniversary = together.replace(year=today.year + 1)

    days_until = (next_anniversary - today).days

    return year_count, days_since, days_until

def get_weekday():
    week_map = ["一", "二", "三", "四", "五", "六", "日"]
    return "星期" + week_map[datetime.today().weekday()]

def get_ai_message(prompt="用温柔的方式说一句不超过10字的话给男朋友鼓励他"):
    print("Generating AI message from Hugging Face...")

    url = "https://router.huggingface.co/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": HF_MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 40,
        "temperature": 0.9,
        "top_p": 0.95
    }

    response = requests.post(url, headers=headers, json=payload, timeout=60)

    # 🛟 Safety check before parsing JSON
    if response.status_code != 200:
        print("HF Status Error:", response.status_code, response.text)
        return "今天也超级爱你 ❤️"

    result = response.json()

    try:
        return result["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print("HF Parse Error:", result)
        return "今天也超级爱你 ❤️"

def send_message(OPENID, ai_msg):
    token = get_access_token()
    year_count, days_since, days_until = date_counters()
    weekday = get_weekday()
    # ai_msg = get_ai_message().strip('"')

    url = f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={token}"

    data = {
        "touser": OPENID,
        "template_id": TEMPLATE_ID,
        "data": {
            "weekday": {"value": weekday},
            "year": {"value": year_count+1},
            "until": {"value": days_until},
            "since": {"value": days_since},
            "ai": {"value": ai_msg}
        }
    }

    res = requests.post(url, json=data)
    print(res.json())

ai_msg = get_ai_message().strip('"')

for id in user_openids:
    send_message(id, ai_msg)