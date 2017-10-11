from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG']= True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:101060cksnowkey@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(288))
    body = db.Column(db.Text())

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/blog')
def splash():
    blog_id = request.args.get('id')
    if blog_id:
        blog = Blog.query.get(blog_id)

        return render_template('page.html',title=blog.title,body=blog.body,tab_title=blog.title)

    posts = Blog.query.all()

    return render_template('blog.html', tab_title='''Alex's Build-a-Blog''', posts=posts)

@app.route('/newpost', methods=['GET','POST'])
def newpost():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']

        if title and body:
            blog = Blog(title=title, body=body)
            db.session.add(blog)
            db.session.commit()

            return redirect('/blog?id={0}'.format(blog.id))

        title_err = ''
        body_err = ''

        if not title:
            title_err = 'Please fill in the title'

        if not body:
            body_err = 'Please fill in the body'

        return render_template('newpost.html', title=title, body=body, title_err=title_err, body_err=body_err, tab_title='''Add a Blog Entry''')
    else:
        return render_template('newpost.html',tab_title='''Add a Blog Entry''')

if __name__ == '__main__':
    app.run()