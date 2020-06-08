import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'thisisasecret'

db = SQLAlchemy(app=app)


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)


def get_weather_data(city):
    website = 'https://api.openweathermap.org/data'
    version = '2.5'
    unit = 'metric'
    api = '8b29b1101ffeda5bb8c2d72994e14df5'

    url = f"{website}/{version}/weather?q={city}&units={unit}&appid={api}"
    r = requests.get(url=url).json()

    if r['cod'] == 200:
        weather = {
            'city': r["name"],
            'temperature': r["main"]["temp"],
            'description': r["weather"][0]["description"],
            'icon': r["weather"][0]["icon"],
        }

    else:
        weather = None

    return weather


@app.route('/')
def index():
    weather_data = []

    cities = City.query.all()
    for city in cities:
        weather = get_weather_data(city=city.name)

        if weather:
            weather_data.append(weather)

    return render_template('index.html', weather_data=weather_data)


@app.route('/', methods=['POST'])
def form_data():
    err_msg = ''
    new_city = request.form.get('city')
    new_city.capitalize()

    if new_city:
        existing_city = City.query.filter_by(name=new_city).first()

        if not existing_city:
            new_city_status = get_weather_data(new_city)

            if new_city_status:
                new_city_obj = City(name=new_city.lower())
                db.session.add(new_city_obj)
                db.session.commit()
            else:
                err_msg = 'City does not exist in the world!!'
        else:
            err_msg = 'City already exist in the database!!'
    else:
        err_msg = 'Please enter a city name!!'

    if err_msg:
        flash(err_msg, 'error')
    else:
        flash('City added succesfully!!', 'success')

    return redirect(url_for('index'))


@app.route('/delete/<name>')
def delete_city(name):
    try:
        city = City.query.filter_by(name=name.lower()).first()
        db.session.delete(city)
        db.session.commit()

        success_msg = f'Successfully deleted {name}!!'

        flash(success_msg, 'success')

    except Exception as e:
        flash(f'{city} not found in database!', 'error')
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
