from flask import Flask, render_template, session, redirect, url_for, request
from flask_session import Session
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy
from constants import *
import csv

app = Flask(__name__)
app.config["SESSION_TYPE"] = 'filesystem'
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+pymysql://fantasy_baseball:password@localhost/fantasy_baseball'
Session(app)
manager = Manager(app)

db = SQLAlchemy()
db.init_app(app)


class Player(db.Model):
    id = db.Column(db.String(256), primary_key=True)
    name = db.Column(db.String(256))
    team = db.Column(db.String(256))
    league = db.Column(db.String(256))
    games = db.Column(db.Integer)
    at_bats = db.Column(db.Integer)
    runs = db.Column(db.Integer)
    hits = db.Column(db.Integer)
    doubles = db.Column(db.Integer)
    triples = db.Column(db.Integer)
    home_runs = db.Column(db.Integer)
    rbis = db.Column(db.Integer)
    stolen = db.Column(db.Integer)
    caught = db.Column(db.Integer)
    walks = db.Column(db.Integer)
    strikeout = db.Column(db.Integer)
    hbp = db.Column(db.Integer)
    sf = db.Column(db.Integer)
    ibb = db.Column(db.Integer)
    available = db.Column(db.Boolean, nullable=False, default=True)


with app.app_context():
    db.create_all()


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        redirectTo = request.args.get('redirectTo')
        if redirectTo is None or redirectTo == '':
            redirectTo = '/'
        return render_template('login.html', redirectTo=redirectTo)
    elif request.method == 'POST':
        user_nm = request.form.get('username')
        passwd = request.form.get('password')
        redirectTo = request.form.get('redirectTo')
        print(f"Login for {user_nm} with {passwd}, redirecting to {redirectTo}")
        if redirectTo is None or redirectTo == '':
            redirectTo = '/'
        session[USER_KEY] = user_nm
        return redirect(redirectTo)


@app.route('/')
@app.route('/home', methods=['GET'])
def showHome():
    if USER_KEY in session:
        user = session[USER_KEY]
        return render_template('home.html', user=user)
    else:
        # show login
        return redirect(url_for('login', redirectTo='/'))


@app.route('/standings')
def standings():
    return render_template('standings.html')


@app.route('/scoreboard')
def scoreboard():
    return render_template('scoreboard.html')


@app.route('/add-players')
def add_players():
    return render_template('add_players.html')


@app.route('/draft-room', methods=['GET', 'POST'])
def draft_room():
    if request.method == 'GET':
        playerList = db.session.execute(db.select(Player).order_by(Player.name))
        return render_template('draft_room.html', playerList=playerList)
    elif request.method == "POST":
        playerToAdd = request.form['addPlayer']
        print(f'adding player id={playerToAdd} to roster')


@app.route('/my-team')
def my_team2():
    return render_template('my_team.html')


#@app.route('/test')
#def test():
    #return render_template('test.html')


@app.route('/points-breakdown')
def points():

    return render_template('points.html')

@manager.command()
def load_players(file_name = 'static/csv/updated-batters.csv'):
    with open(file_name) as csv_file:
        reader = csv.reader(csv_file, delimiter=',')
        line_cnt = 0
        player_list = []
        for row in reader:
            if line_cnt == 0:
                # this is the names of the columns
                cols = list(row)
            else:
                # add the player to the database
                for i in range(len(row)):
                    new_player = Player(id=row[18], name=row[0], team=row[1], league=row[2], games=row[3],
                                        at_bats=row[4], runs=row[5], hits=row[6], doubles=row[7], triples=row[8],
                                        home_runs=row[9], rbis=row[10], stolen=row[11], caught=row[12], walks=row[13],
                                        strikeout=row[14], hbp=row[15], sf=row[16], ibb=row[17])
                    player_list.append(new_player)
            line_cnt += 1
        db.session.add_all(player_list)
        db.session.commit()
    print('added players')


if __name__ == '--main__':
    manager.run()
