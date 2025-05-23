from datetime import datetime
from flask import render_template, flash, redirect, url_for, request,g, jsonify, Flask
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from flask_babel import _, get_locale
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm, \
    ResetPasswordRequestForm, ResetPasswordForm, ProductForm, WorkshopForm, FeedbackForm, ReturnForm, RecycleStoreForm, RecruitmentForm
from app.models import User, Post, Product, WorkshopSubmission, Feedback, Return, RecycleStore, Applicant
from app.email import send_password_reset_email
from flask_uploads import IMAGES, UploadSet
from werkzeug.utils import secure_filename
from sqlalchemy.exc import IntegrityError
from .models import Branch, PersonalApplication, OrganizationApplication
from .forms import RegionForm, PersonalForm, OrganizationForm
from datetime import datetime


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    g.locale = str(get_locale())

#################################################################
# Cookies

@app.before_request
def handle_form_cookies():
    if request.method == 'POST':
        g.cookies_to_set = {  # 改用字典结构
            'form_submission': {
                'value': 'true',
                'max_age': 3600,
                'httponly': True
            }
        }

@app.after_request
def apply_cookies(response):
    if hasattr(g, 'cookies_to_set'):
        for name, params in g.cookies_to_set.items():
            response.set_cookie(name, **params)
    return response
##################################################################

@app.route('/', methods=['GET', 'POST'])
@app.route('/main_index', methods=['GET', 'POST'])
def main():
    return render_template('main_index.html.j2', title='MUJI HK')


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


#Likko - Product
@app.route('/product')
def product():
    return render_template('product.html.j2', title='Product')

#Likko - ProductForm (employee)
@app.route('/employee', methods=['GET', 'POST'])
def employee():
    form = ProductForm()
    if form.validate_on_submit():  # Check if the form is submitted and valid
        # Create or update the product entry in the database
        product = Product.query.filter_by(name=form.name.data).first()
        if product is not None:
            # Update existing product
            product.id = form.id.data
            product.name = form.name.data
            product.price = form.price.data
            product.description = form.description.data
            product.stock = form.stock.data
            product.image = form.image.data.filename if form.image.data else product.image
        else:
            # Add new product
            product = Product(
                id=form.id.data,
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

#Likko - Reference for pure file upload
@app.route("/upload", methods=['GET', 'POST'])
def upload():
    if request.method == 'POST' and 'photo' in request.files:
        photos = UploadSet("photos", IMAGES)
        photos.save(request.files['photo'])
        flash("Photo saved successfully.")
        return render_template('upload.html.j2')
    return render_template('upload.html.j2')

#Likko - Reference for Product Search
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

#Likko - Return Form
@app.route('/return_form', methods=['GET', 'POST'])
def return_form():
    form = ReturnForm()
    if form.validate_on_submit():
        # Create a new return entry in the database
        return_entry = Return(
            username=form.username.data,
            product_id=form.product_id.data,
            receipt_no=form.receipt_no.data,
            reason=form.reason.data,
            policy=form.policy.data
        )
        db.session.add(return_entry)
        db.session.commit()
        flash('Return request submitted successfully!')
        return redirect(url_for('product'))
    return render_template('return_form.html.j2', title='Return Form', form=form)

#Likko - View for Table Entries Update
@app.route('/view_return')
def show_returns():
    returns = Return.query.all()
    return render_template('view_return.html.j2', returns=returns)

@app.route('/view_product')
def show_products():
    products = Product.query.all()
    return render_template('view_product.html.j2', products=products)

#Likko - Recycle Store Form
@app.route('/recycle_form', methods=['GET', 'POST'])
def recycle_form():
    form = RecycleStoreForm()
    if form.validate_on_submit():
        # Create a new recycle store entry in the database
        recycle_store_entry = RecycleStore(
            branch_name=form.branch_name.data,
            address=form.address.data,
            bus_hour=form.bus_hour.data,
            cycle_items=form.cycle_items.data
        )
        db.session.add(recycle_store_entry)
        db.session.commit()
        flash('Recycle store entry submitted successfully!')
        return redirect(url_for('recycle_form'))
    return render_template('recycle_form.html.j2', title='Recycle Store Form', form=form)

#Likko - MUJI Cycle
@app.route('/mujigreen', methods=['GET'])
def mujigreen():
    cycle_stores = RecycleStore.query.all()
    return render_template('mujigreen.html.j2', title='MUJI CYCLE', cycle_stores=cycle_stores)


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

@app.route('/recruitment_form', methods=['GET', 'POST'])
def recruitment_form():
    form = RecruitmentForm()
    
    if form.validate_on_submit():
        print("表单验证通过")  # 调试输出
        # 檢查 email 是否已存在
        existing_applicant = Applicant.query.filter_by(email=form.email.data).first()
        if existing_applicant:
            flash('此電子郵件已提交過申請，請使用其他郵件！', 'error')
            return redirect(url_for('recruitment_form'))
        
        # 嘗試提交申請
        try:
            applicant = Applicant(
                name=form.name.data,
                email=form.email.data,
                position=form.position.data,
                experience=form.experience.data,
                branch_id=form.branch.data.id 
            )
            db.session.add(applicant)
            db.session.commit()
            flash('申請已提交成功！', 'success')
            return redirect(url_for('recruitment_thankyou'))  # 導向感謝頁面
        except IntegrityError:
            db.session.rollback()  # 回滾避免髒資料
            flash('提交失敗：電子郵件已被使用！', 'error')
        except Exception as e:
            db.session.rollback()  # 其他錯誤也回滾
            flash('提交過程中發生錯誤，請稍後再試！', 'error')
        
        return redirect(url_for('recruitment_form'))  # 錯誤時重新導向
    
    return render_template('recruitment_form.html.j2', form=form)

@app.route('/recruitment_thankyou')
def recruitment_thankyou():
    return render_template('recruitment_thankyou.html.j2')


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
  
@app.route('/location', methods=['GET', 'POST'])
def location():  
    # Handle form submission
    if request.method == 'POST':
        region = request.form.get('region')  # Get the selected region from the form
        branches = Branch.query.filter_by(region=region).all()  # Query branches by region
        
        # If the request is an AJAX request, return JSON data
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify([{'name': branch.name} for branch in branches])
        
        # Render the template with the filtered branches
        return render_template('location.html.j2', branches=branches)
    
    # Render the template with no branches initially
    return render_template('location.html.j2', branches=None)

@app.route('/location_form', methods=['GET', 'POST'])
def location_form():
    form = RegionForm()
    if form.validate_on_submit():
        branch = Branch(
        id=form.id.data,
        name=form.name.data,
        region=form.region.data,
        )
        db.session.add(branch)
        db.session.commit()
        flash(_('Branch Updated!'))
        return redirect(url_for('location_form'))
    return render_template('location_form.html.j2', title='location_form', form=form)

@app.route('/apply')
def apply():
     return redirect(url_for('apply_personal'))

@app.route('/apply/personal', methods=['GET', 'POST'])
def apply_personal():
    form = PersonalForm()
    if form.validate_on_submit():
        application = PersonalApplication(
            name=form.name.data,
            phone=form.phone.data,
            email=form.email.data,
            location=form.location.data,
            preferred_date=form.preferred_date.data,
            apply_date=datetime.now()
        )
        db.session.add(application)
        db.session.commit()
        return redirect(url_for('view_applications'))
    return render_template('apply.html.j2', form=form, form_type='personal')

@app.route('/apply/organization', methods=['GET', 'POST'])
def apply_organization():
    form = OrganizationForm()
    if form.validate_on_submit():
        application = OrganizationApplication(
            contact_name=form.contact_name.data,
            brand_name=form.brand_name.data,
            phone=form.phone.data,
            email=form.email.data,
            location=form.location.data,
            preferred_date=form.preferred_date.data,
            apply_date=datetime.now()
        )
        db.session.add(application)
        db.session.commit()
        return redirect(url_for('view_applications'))
    return render_template('apply.html.j2', form=form, form_type='organization')

@app.route('/applications')
def view_applications():
    personal = PersonalApplication.query.all()
    organizations = OrganizationApplication.query.all()
    return render_template('applications.html.j2',
                          personal=personal,
                          organizations=organizations)