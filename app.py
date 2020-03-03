from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import random
from RWJ import read_json, write_json
from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired
import datetime


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

profiles = read_json('data.json')

CSRF_ENABLED = True
app.secret_key = 'my-secret-key-for-flask-teacher-progect'


class Teachers(db.Model):
    __tablename__ = 'teachers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    about = db.Column(db.String(1100), unique=True, nullable=False)
    rating = db.Column(db.Float, nullable=False, default=0.0)
    picture = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    teacher_relations = db.relationship('Booking', back_populates='booking_relations')


class TeachersGoals(FlaskForm):
    id = IntegerField('id')
    goal = StringField('goal')
    name = StringField('name')
    about = StringField('about')
    rating = FloatField('rating')
    picture = StringField('picture')
    price = IntegerField('price')


class Select(db.Model):
    __tablename__ = 'requests'
    id = db.Column(db.Integer, primary_key=True)
    date_add = db.Column(db.Date, default=datetime.date.today(), nullable=False)
    goal = db.Column(db.String(10), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    user_name = db.Column(db.String(20), nullable=False)
    user_phone = db.Column(db.String(16), nullable=False)
    call_user = db.Column(db.Boolean, default=False)
    
    
class SelectForm(FlaskForm):
#    date_add = datetime.date.today()
    goal = StringField('goal')
    time = StringField('time')
    user_name = StringField('user_name', validators=[DataRequired()])
    user_phone = StringField('user_phone', validators=[DataRequired()])
    call_user = False


class Booking(db.Model):
    __tablename__ = 'booking'
    id = db.Column(db.Integer, primary_key=True)
    date_add = db.Column(db.Date, default=datetime.date.today(), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    day = db.Column(db.String(3), nullable=False)
    time = db.Column(db.String(2), nullable=False)
    user_name = db.Column(db.String(20), nullable=False)
    user_phone = db.Column(db.String(16), nullable=False)
    call_user = db.Column(db.Boolean, default=False)
    booking_relations = db.relationship('Teachers', back_populates='teacher_relations')


class BookingForm(FlaskForm):
#    date_add = datetime.date.today()
    teacher_id = StringField('teacher_id')
    day = StringField('day', validators=[DataRequired()])
    time = StringField('time', validators=[DataRequired()])
    user_name = StringField('user_name', validators=[DataRequired()])
    user_phone = StringField('user_phone', validators=[DataRequired()])
    call_user = False

'''
# скрипт для первой загрузки данных, запускать один раз
# в базе таблица teachers без полей goals и free, они в json
db.create_all()

profiles = read_json('data_old.json')

for item in profiles['teachers']:
    teacher = Teachers(name=item['name'], about=item['about'], rating=item['rating'], picture=item['picture'], price=item['price'])
    db.session.add(teacher)
db.session.commit()
'''


@app.route('/', methods=['GET', 'POST'])
@app.route('/index/', methods=['GET', 'POST'])
def main():
    form = TeachersGoals()
    goal_all = profiles['goals']
    teachers = db.session.query(Teachers).all()
    
    if request.method == 'POST':
        select_goal = request.form['goal']
        teacher_all = profiles['teachers']
        teacher_for_goal = []        

        for g in goal_all:
            goal = ''
            if select_goal == g:
                goal = goal_all[g]

                for item in teacher_all:

                    if select_goal in item['goals']:
                        teacher_for_goal.append(item['id'])
                      
                print(teacher_for_goal)
                goal_page = render_template('goal.html', goal=goal, profiles=profiles, teachers=teachers, teacher_for_goal=teacher_for_goal)
                return goal_page
        
    else:    
        choice_teachers = random.sample(teachers, 6)
        main_page = render_template('index.html', choice_teachers=choice_teachers, profiles=profiles, goal=goal_all)
        return main_page
    
    
@app.route('/profiles/<int:id>/', methods=['GET', 'POST'])
def profile(id):
    teachers = db.session.query(Teachers).all()
    profile_page = render_template('profile.html', id=id, teachers=teachers, profiles=profiles)
    return profile_page


@app.route('/booking/<int:id>/<day>/<time>/', methods=['GET', 'POST'])
def booking(id, day, time):
    form = BookingForm()
    booking = Booking()
    teachers = db.session.query(Teachers).all()
    
    teacher_id = id
    day = day
    time = time
    print(day, time, teacher_id)

    if request.method == 'POST':
        user_name = request.form['user_name']
        user_phone = request.form['user_phone']
        
        form.populate_obj(booking)
            
        db.session.add(booking)
        db.session.commit()

        booking_done_page = render_template('booking_done.html', id=teacher_id, day=day, time=time, user_name=user_name, user_phone=user_phone, teachers=teachers, profiles=profiles)
        return booking_done_page
    
    else: 
        booking_page = render_template('booking.html', id=id, day=day, time=time, profiles=profiles, teachers=teachers)
        return booking_page
        


@app.route('/select_teacher/', methods=['GET', 'POST'])
def select_teacher():
    form = SelectForm()
    select = Select()

    if request.method == 'POST':
        goal = request.form['goal']
        time = request.form['time']
        user_name = form.user_name.data
        user_phone = form.user_phone.data
        
        form.populate_obj(select)
            
        db.session.add(select)
        db.session.commit()

        select_done_page = render_template('select_done.html', goal=goal, time=time, user_name=user_name, user_phone=user_phone)
        return select_done_page
        
    else:    
        select_teacher_page = render_template('select_teacher.html', profiles=profiles, form=form, select=select)
        return select_teacher_page


@app.errorhandler(404)
def not_found(e):
    return 'У нас такого нет. Попробуйте вернуться на главную и выбрать что-то другое.'


@app.errorhandler(500)
def server_error(e):
    return 'Что-то не так, но мы ЭТО уже скоро починим.'


if __name__ == '__main__':
    app.run()


