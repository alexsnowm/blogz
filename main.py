from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG']= True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:101060cksnowkey@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(288))
    body = db.Column(db.Text())
    owner_id = db.Column(db.Integer,db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(288),unique=True)
    password = db.Column(db.String(288))
    blogs = db.relationship('Blog',backref='owner')

    def __init__(self, username, password):
        self.username=username
        self.password=password

@app.before_request
def require_login():
    allowed_routes = ['login','list_blogs','index','signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/blog')
def list_blogs():
    blog_id = request.args.get('id')
    owner_id = request.args.get('user')

    if blog_id:
        blog = Blog.query.get(blog_id)

        return render_template('page.html',blog=blog)

    if owner_id:
        owner_posts = Blog.query.filter_by(owner_id=owner_id)

        return render_template('singleUser.html',posts=owner_posts)

    posts = Blog.query.all()

    return render_template('blog.html',posts=posts)

@app.route('/newpost', methods=['GET','POST'])
def newpost():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']

        if title and body:
            owner = User.query.filter_by(username=session['username']).first()

            blog = Blog(title=title, body=body, owner=owner)
            db.session.add(blog)
            db.session.commit()

            return redirect('/blog?id={0}'.format(blog.id))

        title_err = ''
        body_err = ''

        if not title:
            title_err = 'Please fill in the title'

        if not body:
            body_err = 'Please fill in the body'

        return render_template('newpost.html', title=title, body=body, title_err=title_err, body_err=body_err)
    else:
        return render_template('newpost.html')

@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        user_err = ''
        pass_err = ''
        verify_err = ''

        user = User.query.filter_by(username=username).first()
        if user:
            user_err = 'A user with that username already exists'

        if (not username) or (len(username) < 3):
            user_err = '''That's not a valid username'''

        if (not password) or (len(password) < 3):
            pass_err = '''That's not a valid password'''

        if password != verify:
            verify_err = '''Passwords don't match'''

        if not user_err and not pass_err and not verify_err:
            new_user = User(username,password)
            db.session.add(new_user)
            db.session.commit()

            session['username'] = username

            return redirect('/newpost')

        return render_template('signup.html',username=username,user_err=user_err,pass_err=pass_err,verify_err=verify_err)

    return render_template('signup.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user:
            if password == user.password:
                session['username'] = username
                
                return redirect('/newpost')
            flash('Invalid password','error')
        else:
            flash('Invalid username','error')

        return redirect('/login')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/')
def index():
    users = User.query.all()

    return render_template('index.html',users=users)

app.secret_key = 'y337kGcys&zP3B'

if __name__ == '__main__':
    app.run()