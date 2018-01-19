import datetime

import os
from flask import Flask, request, abort,render_template,session,redirect,url_for
from flask import flash
from flask_script import  Manager,Shell
#使用script来管理App
from flask_migrate import Migrate,MigrateCommand
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import Form
from wtforms import StringField,SubmitField
from wtforms.validators import Required
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail

basedir = os.path.abspath(os.path.dirname(__file__))


app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess'
#设置加密密钥
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+os.path.join(basedir,'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
#配置数据库
bootstarp = Bootstrap(app)
moment = Moment(app)
manager = Manager(app)
migrate = Migrate(app,db)
manager.add_command('db',MigrateCommand)
#添加migrate扩展


app.config['MAIL_SERVER'] = 'smtp.139.com'
app.config['MAIL_PORT'] = 25
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = '183556852040@139.com'
app.config['MAIL_PASSWORD'] = ''
mail = Mail(app)

@app.route('/',methods=['GET','POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username = form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            session['known'] = False
        else:
            session['known'] = True
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('index'))
    return render_template('index.html',
                           form=form, name=session.get('name'),
                           known = session.get('known',False))
# def index():
#     # user_agent = request.headers.get('User-Agent')
#     name = None
#     form = NameForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(username=form.name.data).first()
#         old_name = session.get('name')
#         if old_name is not None and old_name != form.name.data:
#             flash('you change name')
#         session['name'] = form.name.data
#         #使用session来进行处理
#         return redirect(url_for('index'))
#     # return render_template('index.html', current_time = datetime.datetime.utcnow())
#     return render_template('index.html',form = form,name = session.get('name'))

#传递参数
@app.route('/user/<name>')
def user(name):
    return render_template('user.html',name=name)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'),500


class NameForm(Form):
    name = StringField('what is your name',validators=[Required()])
    submit = SubmitField('submit')

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64),unique=True)
    users = db.relationship('User',backref='role',lazy='dynamic')  #设置关系

    def __repr__(self):
        return 'Role %s'%self.name

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(64),unique=True)
    role_id = db.Column(db.Integer,db.ForeignKey('roles.id'))  #设置外键

    def __repr__(self):
        return 'User %s'%self.username

def make_shell_context():
    return dict(app=app,db=db,User=User,Role=Role)
manager.add_command('shell',Shell(make_context=make_shell_context))
#为shell添加上下文


if __name__ == '__main__':
    # app.run(debug=True)
    manager.run()