from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
    TextAreaField, FileField #import additional FileField for product image
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, \
    Length
from app.models import User

# Likko's Part: ProductForm for Product Entries
class ProductForm(FlaskForm):
    product_id = StringField('Product ID', validators=[DataRequired()])
    product_name = StringField('Product Name', validators=[DataRequired()])
    product_price = StringField('Product Price', validators=[DataRequired()])
    product_description = TextAreaField('Product Description', validators=[Length(min=0, max=140)])
    product_stock = StringField('Product Stock', validators=[DataRequired()])
    product_image = FileField('Product Image')
    submit = SubmitField('Update Product')

    def validate_product_name(self, product_name):
        product = User.query.filter_by(username=product_name.data).first()
        if product is not None:
            raise ValidationError('Please use a different product name.')
    def validate_product_price(self, product_price):
        if not product_price.data.isdigit():
            raise ValidationError('Please enter a valid price.')
        if float(product_price.data) <= 0:
            raise ValidationError('Price must be greater than zero.')
    def validate_product_image(self, product_image):
        #print(product_image)
        #print(product_image.data.filename)
        if not product_image.data.filename.endswith('.jpg', '.jpeg', '.png'):
            raise ValidationError('Only file formats .jpg, .jpeg, or .png are allowed.')

##########################################

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
