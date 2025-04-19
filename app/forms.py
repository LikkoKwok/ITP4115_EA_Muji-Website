from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
    TextAreaField, SelectField, FileField #import additional FileField for product image
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, \
    Length
from app.models import User

# Likko's Part: ProductForm for Product Entries
class ProductForm(FlaskForm):
    id = StringField('Product ID', validators=[DataRequired()])
    name = StringField('Product Name', validators=[DataRequired()])
    price = StringField('Product Price', validators=[DataRequired()])
    description = TextAreaField('Product Description', validators=[Length(min=0, max=140)])
    stock = StringField('Product Stock', validators=[DataRequired()])
    image = FileField('Product Image')
    submit = SubmitField('Update Product')

    def validate_product_name(self, name):
        product = User.query.filter_by(name=name.data).first()
        if product is not None:
            raise ValidationError('Please use a different product name.')
    def validate_product_price(self, price):
        if not price.data.isdigit():
            raise ValidationError('Please enter a valid price.')
        if float(price.data) <= 0:
            raise ValidationError('Price must be greater than zero.')
    def validate_product_image(self, image):
        if not image.data.filename.endswith('.jpg', '.jpeg', '.png'):
            raise ValidationError('Only file formats .jpg, .jpeg, or .png are allowed.')

##########################################

# Workshop_submit_form

class WorkshopForm(FlaskForm):
    name = StringField('姓名', validators=[DataRequired(message="※ 請填寫姓名"),
    ], render_kw={"placeholder": "請輸入完整姓名"})

    email = StringField('電郵', validators=[DataRequired(message="※ 請填寫郵箱"),
        Email(message="※ 郵箱格式不正確")
    ], render_kw={"placeholder": "example@domain.com"})

    project = SelectField('報名項目', validators=[DataRequired(message="※ 請選擇工作坊")
    ], choices=[
        ('workshop1', '香薰香水調配工作坊'),
        ('workshop2', '動物拼貼畫冊工作坊'),
        ('workshop3', 'What is MUJI Exhibition')
    ], render_kw={"class": "dropdown"})

    submit = SubmitField('提交', render_kw={"class": "submit-btn"})

# feedback_form

class FeedbackForm(FlaskForm):
    name = StringField('姓名', validators=[
        DataRequired(message="必须填写姓名"),
        Length(max=80)
    ], render_kw={
        "placeholder": "请输入全名",
        "autocomplete": "name"
    })
    
    email = StringField('电子邮箱', validators=[
        DataRequired(message="必须填写邮箱"),
        Email(message="无效的邮箱格式"),
        Length(max=120)
    ], render_kw={
        "placeholder": "example@domain.com",
        "autocomplete": "email"
    })
    
    message = TextAreaField('反馈意见', validators=[
        DataRequired(message="必须填写内容"),
        Length(min=10, max=500)
    ], render_kw={
        "placeholder": "请输入至少10个字符",
        "autocomplete": "off",
        "rows": 5
    })
    
    submit = SubmitField('提交反馈')

############################################
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(),
                                           EqualTo('password')])
    submit = SubmitField('Request Password Reset')


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')


class PostForm(FlaskForm):
    post = TextAreaField('Say something', validators=[DataRequired()])
    submit = SubmitField('Submit')

class RegionForm(FlaskForm):
    region = SelectField('選擇區域', choices=[  
        ('', '請選擇'),
        ('new_territories', '新界'),
        ('kowloon', '九龍'),
        ('hong_kong_island', '香港島')
    ], validators=[DataRequired()])