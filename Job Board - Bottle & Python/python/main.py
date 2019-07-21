__author__ = 'Steve Cassidy'

from bottle import Bottle,request, response, template, redirect, static_file
import sqlite3
import users
import interface
app = Bottle()


@app.route('/')
def index(db):

    # Get the top 10 users
    job_id = interface.position_list(db, 10)
    info = {
       'positions': job_id
    }
    name = users.session_user(db)
    if users.session_user(db) :
        nick = {'nick': name}
        return template('index_login.html', nick)
    else:
     return template('index.html', info)


@app.route('/positions/<id>')
def positions(db,id):
    data1 ={
        'description': interface.position_get(db, id)
    }
    return template('positions.html', data1)

@app.route('/login',method='post')
def test_login(db):
    nickname = request.forms.get('nick')
    password = request.forms.get('password')
    if users.check_login(db, nickname, password):
        users.generate_session(db, nickname)
        redirect('/')
    else:
        return template('error_login.html')

@app.route('/logout')

def logout(db):
    usernick = users.session_user(db)
    users.delete_session(db, usernick)
    redirect('/')




@app.route('/static/<filename:path>')
def static(filename):
    return static_file(filename=filename, root='static')


if __name__ == '__main__':
    from bottle.ext import sqlite
    from database import DATABASE_NAME

    # install the database plugin
    app.install(sqlite.Plugin(dbfile=DATABASE_NAME))

    # Run the Web App
    app.run(debug=True, port=8010)
