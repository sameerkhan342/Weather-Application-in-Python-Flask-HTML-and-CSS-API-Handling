# app.py
from flask import Flask, render_template, request
import requests
from datetime import datetime, timezone, timedelta

app = Flask(__name__)

API_KEY = "YOUR_API_KEY"

def fetch_weather(city):
    url = "https://api.openweathermap.org/data/2.5/weather"
    r = requests.get(url, params={"q": city, "appid": API_KEY, "units": "metric"})
    if r.status_code != 200:
        try:
            msg = r.json().get("message", "error")
        except Exception:
            msg = "error"
        return None, msg
    return r.json(), None

def fmt_time(ts, offset):
    return datetime.fromtimestamp(ts, tz=timezone(timedelta(seconds=offset))).strftime("%b %d, %I:%M %p")

@app.route("/", methods=["GET", "POST"])
def index():
    default_city = "Karachi"
    city = default_city
    if request.method == "POST":
        city = (request.form.get("city") or "").strip() or default_city
    elif request.args.get("city"):
        city = request.args.get("city").strip()
    data, error = fetch_weather(city)
    view = None
    if data:
        tz = data.get("timezone", 0)
        sys = data.get("sys", {})
        main = data.get("main", {})
        wind = data.get("wind", {})
        weather = (data.get("weather") or [{}])[0]
        clouds = data.get("clouds", {}).get("all")
        visibility = data.get("visibility")
        icon = weather.get("icon")
        icon_url = f"https://openweathermap.org/img/wn/{icon}@2x.png" if icon else None
        view = {
            "city": f'{data.get("name","")}, {sys.get("country","")}'.strip(", "),
            "temp": round(main.get("temp", 0)),
            "feels_like": round(main.get("feels_like", 0)),
            "desc": weather.get("description","").title(),
            "icon_url": icon_url,
            "humidity": main.get("humidity"),
            "pressure": main.get("pressure"),
            "wind": wind.get("speed"),
            "gust": wind.get("gust"),
            "sunrise": fmt_time(sys.get("sunrise", 0), tz) if sys.get("sunrise") else None,
            "sunset": fmt_time(sys.get("sunset", 0), tz) if sys.get("sunset") else None,
            "time": fmt_time(data.get("dt", 0), tz) if data.get("dt") else None,
            "clouds": clouds,
            "visibility": f"{round((visibility or 0)/1000,1)} km" if visibility else None,
        }
    return render_template("index.html", city_query=city, view=view, error=error)

if __name__ == "__main__":
    app.run(debug=True)
