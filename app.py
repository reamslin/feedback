from flask import Flask, redirect, render_template, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from forms import RegisterForm, LoginForm, FeedbackForm
from models import db, connect_db, User, Feedback

app = Flask(__name__)
app.config['SECRET_KEY'] = "secret"
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///feedback'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

connect_db(app)
db.create_all()


@app.route('/')
def show_homepage():
    return redirect('/register')


@app.route('/register', methods=['GET', 'POST'])
def handle_register():
    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        new_user = User.register(username=username, password=password, email=email,
                                 first_name=first_name, last_name=last_name)

        db.session.add(new_user)
        # check for errors on registering
        db.session.commit()

        session['user_id'] = new_user.id

        return redirect(f'/users/{new_user.id}')

    else:
        return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username=username, password=password)
        if user:
            session['user_id'] = user.id
            return redirect(f'/users/{user.id}')
        else:
            form.username.errors = ["Invalid username/password"]
    return render_template("login.html", form=form)


@app.route('/users/<int:user_id>')
def show_user(user_id):
    if 'user_id' in session:
        user = User.query.get_or_404(user_id)
        return render_template('user.html', user=user)
    else:
        return redirect('/')


@app.route('/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    if 'user_id' in session:
        if session['user_id'] == user_id:
            user = User.query.get_or_404(user_id)
            db.session.delete(user)
            db.session.commit()
            session.pop('user_id')
        else:
            flash('You cannot delete another user')
        return redirect('/')
    else:
        flash('must be logged in to delete account')
        return redirect('/login')


@app.route('/users/<int:user_id>/feedback/add', methods=['GET', 'POST'])
def show_feedback_form(user_id):
    if 'user_id' in session:
        if session['user_id'] == user_id:
            form = FeedbackForm()
            if form.validate_on_submit():
                title = form.title.data
                content = form.content.data
                new_feedback = Feedback(
                    title=title, content=content, user_id=user_id)
                db.session.add(new_feedback)
                db.session.commit()
                flash('feedback added!')
                return redirect(f'/users/{user_id}')
            else:
                return render_template('add_feedback.html', form=form)
        else:
            flash('This is not your account!')
            return redirect('/')
    else:
        flash('You must be logged in to add feedback!')
        return redirect('/login')


# Had an issue with this... prefetching? don't use GET
@app.route('/logout')
def logout():
    if 'user_id' in session:
        session.pop('user_id')

    return redirect('/')


@app.route('/feedback/<int:feedback_id>/update', methods=['GET', 'POST'])
def update_feedback(feedback_id):
    if 'user_id' in session:
        feedback = Feedback.query.get_or_404(feedback_id)
        if session['user_id'] == feedback.user_id:
            form = FeedbackForm(obj=feedback)

            if form.validate_on_submit():
                feedback.title = form.title.data
                feedback.content = form.content.data
                db.session.commit()
                return redirect(f'/users/{feedback.user_id}')
            else:
                return render_template('update_feedback.html', form=form)
        else:
            flash('This feedback is not yours!')
            return redirect(f'/users/{session["user_id"]}')
    else:
        flash('Must be logged in to update feedback!')
        return redirect('/login')


@app.route('/feedback/<int:feedback_id>/delete', methods=['POST'])
def delete_feedback(feedback_id):
    if 'user_id' in session:
        feedback = Feedback.query.get_or_404(feedback_id)
        if session['user_id'] == feedback.user_id:
            db.session.delete(feedback)
            db.session.commit()
            return redirect(f'/users/{feedback.user_id}')
        else:
            flash('This feedback is not yours to delete!')
            return redirect(f'/users/{session["user_id"]}')
    else:
        flash('Must be logged in to delete feedback!')
        return redirect('/login')
