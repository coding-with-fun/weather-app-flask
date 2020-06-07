import requests
from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def index():
    url = "http://samples.openweathermap.org/data/2.5/find?q={}&units=metric&appid=439d4b804bc8187953eb36d2a8c26a02"
    city = "London"

    r = requests.get(url.format(city)).json()

    weather = {
        'city': city,
        'temperature': r["list"][0]["main"]["temp"],
        'description': r["list"][0]["weather"][1]["description"],
        'icon': r["list"][0]["weather"][1]["icon"],
    }

    print(weather)
    return render_template('index.html', weather=weather)


if __name__ == "__main__":
    app.run(debug=True)
