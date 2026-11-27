import os
import json
import http.client
import urllib.parse
from dotenv import load_dotenv

GEMINI_HOST = "generativelanguage" + "." + "googleapis" + "." + "com"
WEATHER_HOST = "api" + "." + "openweathermap" + "." + "org"

def get_weather():
    load_dotenv(override=True)
    weather_key = os.getenv("OPENWEATHER_API_KEY", "").strip()
    city = os.getenv("CITY", "Bengaluru").strip()
    if not weather_key:
        return "24°C, Partly Cloudy (Mocked)"
    try:
        conn = http.client.HTTPSConnection(WEATHER_HOST, timeout=5)
        query = urllib.parse.urlencode({"q": city, "appid": weather_key, "units": "metric"})
        conn.request("GET", f"/data/2.5/weather?{query}")
        res = json.loads(conn.getresponse().read().decode("utf-8"))
        if "main" in res:
            return f"{res['main']['temp']}°C, {res['weather'][0]['description'].title()}"
    except Exception:
        pass
    return "24°C, Clear"

def list_available_models(gemini_key):
    conn = http.client.HTTPSConnection(GEMINI_HOST, timeout=10)
    conn.request("GET", f"/v1beta/models?key={gemini_key}")
    resp = conn.getresponse()
    raw = resp.read().decode("utf-8", errors="replace")
    if resp.status != 200:
        return [], f"ListModels HTTP {resp.status}: {raw[:200]}"
    data = json.loads(raw)
    valid = []
    for m in data.get("models", []):
        if "generateContent" in m.get("supportedGenerationMethods", []):
            name = m.get("name", "")
            if "flash" in name:
                valid.insert(0, name)
            else:
                valid.append(name)
    return valid, None

def generate_briefing():
    load_dotenv(override=True)
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    city = os.getenv("CITY", "Bengaluru").strip()

    if not gemini_key:
        return "GEMINI_API_KEY is missing in .env"

    models_to_try, list_err = list_available_models(gemini_key)
    if list_err:
        return list_err
    if not models_to_try:
        return "No generateContent models enabled for this API key."

    with open("mock_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    weather = get_weather()
    prompt = (
        f"You are Stride, an AI student assistant. Create a concise daily briefing for a student.\n"
        f"Weather in {city}: {weather}\n"
        f"Data: {json.dumps(data)}\n"
        f"Include:\n"
        f"1. Weather snapshot\n"
        f"2. Key email action items & preparation needed\n"
        f"3. Schedule conflict alerts (highlight overlapping times!)\n"
        f"4. Top academic deadlines\n"
        f"Keep it formatted cleanly with bullet points."
    )

    last_error = ""
    body = json.dumps({"contents": [{"parts": [{"text": prompt}]}]})
    headers = {"Content-Type": "application/json"}

    for model_path in models_to_try[:5]:
        conn = http.client.HTTPSConnection(GEMINI_HOST, timeout=20)
        path = f"/v1beta/{model_path}:generateContent?key={gemini_key}"
        conn.request("POST", path, body=body, headers=headers)
        resp = conn.getresponse()
        raw = resp.read().decode("utf-8", errors="replace")
        if resp.status == 200:
            res = json.loads(raw)
            if "candidates" in res:
                return "\n".join(p["text"] for p in res["candidates"][0]["content"]["parts"] if "text" in p and not p.get("thought"))
        last_error = f"{model_path} -> HTTP {resp.status}: {raw[:200]}"

    return f"Tried {models_to_try[:5]}. Last error: {last_error}"
