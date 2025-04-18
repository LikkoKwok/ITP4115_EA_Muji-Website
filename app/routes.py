from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from flask_babel import _, get_locale
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm, \
    ResetPasswordRequestForm, ResetPasswordForm, ProductForm, WorkshopForm, FeedbackForm
from app.models import User, Post, Product, WorkshopSubmission, Feedback
from app.email import send_password_reset_email
from flask_uploads import IMAGES, UploadSet
from werkzeug.utils import secure_filename



@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    g.locale = str(get_locale())


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash(_('Your post is now live!'))
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page=page, per_page=app.config["POSTS_PER_PAGE"], error_out=False)
    next_url = url_for(
        'index', page=posts.next_num) if posts.next_num else None
    prev_url = url_for(
        'index', page=posts.prev_num) if posts.prev_num else None
    return render_template('index.html.j2', title=_('Home'), form=form,
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)

#Likko's Part: Product
@app.route('/product')
def product():
    return render_template('product.html.j2', title='Product')

#Likko's Part: ProductForm (employee)
@app.route('/employee', methods=['GET', 'POST'])
def employee():
    form = ProductForm()
    if form.validate_on_submit():  # Check if the form is submitted and valid
        # Create or update the product entry in the database
        product = Product.query.filter_by(name=form.name.data).first()
        if product:
            # Update existing product
            product.price = form.price.data
            product.description = form.description.data
            product.stock = form.stock.data
            product.image = form.image.data.filename if form.image.data else product.image
        else:
            # Add new product
            product = Product(
                name=form.name.data,
                price=form.price.data,
                description=form.description.data,
                stock=form.stock.data,
                image = form.image.data.filename if form.image.data else None
            )
            # Save the uploaded image
            if form.image.data:
                filename = secure_filename(form.image.data.filename)
                form.image.data.save(f'app/static/product_images/{filename}')
                product.image = filename
        # Save the product to the database
        db.session.add(product)
        db.session.commit()  # Save changes to the database
        flash('Product entry has been updated successfully!')
        return redirect(url_for('employee'))
    return render_template('employee.html.j2', title='員工專用', form=form)

#Likko's Reference for pure file upload
@app.route("/upload", methods=['GET', 'POST'])
def upload():
    if request.method == 'POST' and 'photo' in request.files:
        photos = UploadSet("photos", IMAGES)
        photos.save(request.files['photo'])
        flash("Photo saved successfully.")
        return render_template('upload.html.j2')
    return render_template('upload.html.j2')

#Likko's Part: Product Search
@app.route('/search', methods=['GET', 'POST'])
def search():
    query = request.args.get('query', '').strip()  # Get the search query from the URL
    products = []
    if query:
        # Search by ID if the query is numeric
        if query.isdigit():
            products = Product.query.filter_by(id=int(query)).all()
        else:
            # Search by name (case-insensitive)
            products = Product.query.filter(Product.name.ilike(f'%{query}%')).all()
    return render_template('search.html.j2', title=_('Search Products'), products=products, query=query)




@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=app.config["POSTS_PER_PAGE"], error_out=False)
    next_url = url_for(
        'explore', page=posts.next_num) if posts.next_num else None
    prev_url = url_for(
        'explore', page=posts.prev_num) if posts.prev_num else None
    return render_template('index.html.j2', title=_('Explore'),
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(_('Invalid username or password'))
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html.j2', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('Congratulations, you are now a registered user!'))
        return redirect(url_for('login'))
    return render_template('register.html.j2', title='Register', form=form)


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash(
            _('Check your email for the instructions to reset your password'))
        return redirect(url_for('login'))
    return render_template('reset_password_request.html.j2',
                           title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if user is None:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been reset.'))
        return redirect(url_for('login'))
    return render_template('reset_password.html.j2', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.followed_posts().paginate(
        page=page, per_page=app.config["POSTS_PER_PAGE"], error_out=False)
    next_url = url_for(
        'index', page=posts.next_num) if posts.next_num else None
    prev_url = url_for(
        'index', page=posts.prev_num) if posts.prev_num else None
    return render_template('user.html.j2', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html.j2', title='Edit Profile',form=form)


@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('index'))
    if user == current_user:
        flash(_('You cannot follow yourself!'))
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following %(username)s!', username=username)
    return redirect(url_for('user', username=username))


@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('index'))
    if user == current_user:
        flash(_('You cannot unfollow yourself!'))
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(_('You are not following %(username)s.', username=username))
    return redirect(url_for('user', username=username))

#recruitment
@app.route('/recruitment')
def recruitment():
    return render_template('recruitment.html.j2')

# Recruitment_form

@app.route('/recruitment_form')
def recruitment_form():
    return render_template('recruitment_form.html.j2')

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    email = request.form['email']
    position = request.form['position']
    experience = request.form['experience']
    # 這裡可以將資料儲存到資料庫或進行其他處理
    return f"感謝 {name} 提交申請！我們會盡快與您聯繫。"

# contact us/ feedback

@app.route('/contact-us')
def contact_us():
    return render_template('contact_us.html.j2')

@app.route('/feedback_form', methods=['GET', 'POST'])
def feedback_form():
        form = FeedbackForm()
        
        if form.validate_on_submit():
            try:
                feedback = Feedback(
                    name=form.name.data,
                    email=form.email.data,
                    message=form.message.data
                )
                db.session.add(feedback)
                db.session.commit()
                flash('反馈已成功提交！', 'success')
                return redirect(url_for('feedback_thankyou'))
            except Exception as e:
                db.session.rollback()
                flash(f'提交失败: {str(e)}', 'danger')
        
        return render_template('feedback_form.html.j2', form=form)

@app.route('/feedback/thankyou')
def feedback_thankyou():
    return render_template('feedback_thankyou.html.j2')


# events

@app.route('/events')
def events():
    return render_template('events.html.j2')

#workshop

@app.route('/perfume_workshop')
def perfume_workshop():
    return render_template('perfume_workshop.html.j2')

@app.route('/animal_workshop')
def animal_workshop():
    return render_template('animal_workshop.html.j2')

@app.route('/what_is_muji_workshop')
def what_is_muji_workshop():
    return render_template('what_is_muji_workshop.html.j2')

@app.route('/main_index')
def main_index():
    return render_template('main_index.html.j2')

@app.route('/store')
def store_html():
    return render_template('store.html.j2')

@app.route('/intord')
def intord_html():
    return render_template('intord.html.j2')



# workshop_submit_form

@app.route('/workshop_submit_form', methods=['GET', 'POST'])
def workshop_submit_form():
    form = WorkshopForm()
    
    if form.validate_on_submit():
        # 这里添加数据库操作（示例）
        new_record = WorkshopSubmission(name=form.name.data, email=form.email.data, project=form.project.data)
        db.session.add(new_record)
        db.session.commit()
        return redirect(url_for('workshop_thankyou'))
    
    return render_template('workshop_submit_form.html.j2', form=form)

@app.route('/workshop_thankyou')
def workshop_thankyou():
    return render_template('workshop_thankyou.html.j2')

#Open muji

@app.route('/open_muji')
def open_muji():
    return render_template('open_muji.html.j2')