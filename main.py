from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import func
from flask_sqlalchemy import SQLAlchemy
import sqlite3

db = sqlite3.connect('test.db', check_same_thread=False)
cur = db.cursor()

cur.execute(
    """CREATE TABLE if not exists answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    q1 TEXT,
    q2 TEXT, 
    q3 TEXT,
    q4 TEXT)
    """)

cur.execute(
    """CREATE TABLE if not exists questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT
    )""")

cur.execute(
    """CREATE TABLE if not exists
    user ( 
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    gender TEXT,
    education TEXT,
    age INTEGER )""")

list_of_questions = [('На кого из смешариков вы похожи?',), ('Каким смешариком вы хотели быть в детстве?',), ('Какой смешарик вам нравится больше всего? (хоть они и все замечательные)',), ('Какой смешарик вам не нравится больше всего? (хоть они и все замечательные 2.0)',)]

for smth in list_of_questions:
    cur.execute(
        '''INSERT into questions (text) VALUES (?)''', smth
    )
    cur.execute(
        '''DELETE FROM questions WHERE id>4'''
    )
db.commit()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    gender = db.Column(db.Text)
    education = db.Column(db.Text)
    age = db.Column(db.Integer)


class Questions(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)


class Answers(db.Model):
    __tablename__ = 'answers'
    id = db.Column(db.Integer, primary_key=True)
    q1 = db.Column(db.Integer)
    q2 = db.Column(db.Integer)
    q3 = db.Column(db.Integer)
    q4 = db.Column(db.Integer)

@app.route('/')
def base():
    return render_template("base.html")

@app.route('/questions')
def question_page():
    questions = Questions.query.all()
    return render_template(
        'questions.html',
        questions=questions
    )

@app.route('/process', methods=['get'])
def answer_process():
    if not request.args:
        return redirect(url_for('question_page'))
    gender = request.args.get('gender')
    education = request.args.get('education')
    age = request.args.get('age')
    user = User(
        age=age,
        gender=gender,
        education=education
    )
    db.session.add(user)
    db.session.commit()
    db.session.refresh(user)
    q1 = request.args.get('q1')
    q2 = request.args.get('q2')
    q3 = request.args.get('q3')
    q4 = request.args.get('q4')
    answer = Answers(id=user.id, q1=q1, q2=q2, q3=q3, q4=q4)
    db.session.add(answer)
    db.session.commit()
    return 'Ok'


@app.route('/results')
def results():
    all_info = {}
    age_stats = db.session.query(
        func.avg(User.age),
        func.min(User.age),
        func.max(User.age)
    ).one()
    all_info['age_mean'] = age_stats[0]
    all_info['age_min'] = age_stats[1]
    all_info['age_max'] = age_stats[2]
    all_info['total_count'] = User.query.count()

    q1_answers = db.session.query(Answers.q1).all()
    q2_answers = db.session.query(Answers.q2).all()
    q3_answers = db.session.query(Answers.q3).all()
    q4_answers = db.session.query(Answers.q4).all()
    most_pop1 = cur.execute(
        """SELECT q1
        FROM answers
    GROUP BY q1
    ORDER BY count(*) DESC
       LIMIT 1""")
    all_info['most_popq1'] = most_pop1.fetchall()[0][0]
    most_pop2 = cur.execute(
        """SELECT q1
        FROM answers
    GROUP BY q1
    ORDER BY count(*) DESC
       LIMIT 1""")
    all_info['most_popq2'] = most_pop2.fetchall()[0][0]
    most_pop3 = cur.execute(
        """SELECT q1
        FROM answers
    GROUP BY q1
    ORDER BY count(*) DESC
       LIMIT 1""")
    all_info['most_popq3'] = most_pop3.fetchall()[0][0]
    most_pop4 = cur.execute(
        """SELECT q1
        FROM answers
    GROUP BY q1
    ORDER BY count(*) DESC
       LIMIT 1""")
    all_info['most_popq4'] = most_pop4.fetchall()[0][0]
    return render_template('results.html', all_info=all_info)



if __name__ == '__main__':
    app.run()