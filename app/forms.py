from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
    TextAreaField, SelectField, FileField, SelectMultipleField, DateField #import additional FileField for product image
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, \
    Length
from app.models import User

# Likko - ProductForm
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

# Likko - ReturnForm
class ReturnForm(FlaskForm):
    username = StringField('用戶名稱', validators=[DataRequired()])
    product_id = StringField('商品編號', validators=[DataRequired()])
    receipt_no = StringField('購買收據號碼', validators=[DataRequired()])
    reason = TextAreaField('退款原因 (只適用於退款)')
    policy = SelectField('所需之退/換貨服務', choices=[('換貨', '換貨'), ('退款及退貨', '退款及退貨'), ('退款(無須退貨)', '退款(無須退貨)')])
    submit = SubmitField('提交申請')

    # def validate_product_id(self, product_id):
    #     product = User.query.filter_by(id=product_id.data).first()
    #     if product is None:
    #         raise ValidationError('Invalid Product ID.')
    # def validate_username(self, username):
    #     user = User.query.filter_by(username=username.data).first()
    #     if user is None:
    #         raise ValidationError('Invalid Username.')

##########################################

# Likko - RecycleStoreForm
class RecycleStoreForm(FlaskForm):
    branch_name = StringField('分店', validators=[DataRequired()])
    address = StringField('地址', validators=[DataRequired()])
    bus_hour = StringField('營業時間', validators=[DataRequired()])
    cycle_items = SelectMultipleField('回收物品', choices=['塑膠', '紙', '鋁罐及玻璃瓶', '無印良品衣物'], option_widget=None)   
    submit = SubmitField('輸入')

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

# Recruitment_form
class RecruitmentForm(FlaskForm):
    name = StringField('姓名', validators=[
        DataRequired(message="請輸入姓名"),
        Length(max=50, message="姓名長度過長")
    ])
    
    email = StringField('電子郵件', validators=[
        DataRequired(message="請輸入電子郵件"),
        Email(message="無效的電子郵件格式"),
        Length(max=120)
    ])
    
    position = SelectField('應聘職位', choices=[
        ('', '請選擇職位'),
        ('軟體工程師', '軟體工程師'),
        ('售貨員', '售貨員'),
        ('產品經理', '產品經理'),
        ('倉務員', '倉務員'),
        ('專案經理', '專案經理')
    ], validators=[DataRequired(message="請選擇職位")])
    
    experience = TextAreaField('工作經驗', validators=[
        DataRequired(message="請填寫工作經驗"),
        Length(min=20, message="至少輸入20個字")
    ])


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
    id = StringField('Branch ID', validators=[DataRequired()])
    name = StringField('Branch Name', validators=[DataRequired()])
    region = SelectField('選擇區域', choices=[
        ('', '請選擇'),
        ('new_territories', '新界'),
        ('kowloon', '九龍'),
        ('hong_kong_island', '香港島')
    ], validators=[DataRequired()])
    submit = SubmitField('Submit')

class BaseForm(FlaskForm):
    phone = StringField('聯絡電話', validators=[DataRequired()])
    email = StringField('聯絡電郵', validators=[DataRequired(), Email()])
    location = SelectField('市集地點', choices=[
        ('taipei', '皇室堡'),
        ('taichung', '奧海城'),
        ('kaohsiung', '圍方')
    ])
    preferred_date = DateField('首選日期', format='%Y-%m-%d')
    submit = SubmitField('提交申請')

class PersonalForm(BaseForm):
    name = StringField('申請人姓名', validators=[DataRequired()])

class OrganizationForm(BaseForm):
    contact_name = StringField('聯絡人姓名', validators=[DataRequired()])
    brand_name = StringField('品牌名稱', validators=[DataRequired()])