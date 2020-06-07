import requests
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app=app)

class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)


@app.route('/', methods=['GET', 'POST'])
def index():
    city_set = set()
    weather_data = []
    new_city_flag = False
    city_error = False

    cities = City.query.all()
    for city in cities:
        city_set.add(city.name)

    if request.method == 'POST':
        new_city = request.form.get('city')
        new_city.capitalize()

        if new_city not in city_set:
            city_set.add(new_city)
            new_city_flag = True

    website = 'https://api.openweathermap.org/data'
    version = '2.5'
    unit = 'metric'
    api = '8b29b1101ffeda5bb8c2d72994e14df5'

    for city in city_set:
        url = f"{website}/{version}/weather?q={city}&units={unit}&appid={api}"
        r = requests.get(url=url).json()

        if r['cod'] == 200:
            weather = {
                'city': r["name"],
                'temperature': r["main"]["temp"],
                'description': r["weather"][0]["description"],
                'icon': r["weather"][0]["icon"],
            }
            weather_data.append(weather)
            if new_city_flag is True:
                new_city_object = City(name=city)
                db.session.add(new_city_object)
                db.session.commit()

        else:
            city_error = True

    if city_error:
        city_set.remove(new_city)

    return render_template('index.html', weather_data=weather_data)


if __name__ == "__main__":
    app.run(debug=True)
