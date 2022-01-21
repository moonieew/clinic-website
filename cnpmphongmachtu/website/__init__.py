# Import các thư viện vào
from flask import Flask
from flask_login.config import LOGIN_MESSAGE
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_login import LoginManager

app = Flask(__name__)

# Thiết lập SECRET_KEY cho app
app.config["SECRET_KEY"] = "@#@$@%#^#&*%^(#*&%^*&@*%@(%@"
# Đổi lại root:password theo MYSQL trên máy từng người để có thể tạo database
app.config[
    "SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:1234@localhost/phongmachtu?charset=utf8mb4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

db = SQLAlchemy(app=app)
admin = Admin(app=app, name="QUẢN LÝ PHÒNG MẠCH", template_mode="bootstrap4")
login = LoginManager(app=app)
