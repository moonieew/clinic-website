from flask_admin.contrib.sqla import ModelView
from sqlalchemy.orm import column_property
from website.models import Thuoc, DonVi, CachDung, QuyDinh
from website import db, admin
from flask_admin import BaseView, expose
from flask import session, redirect, url_for

class ThuocModelView(ModelView):
    can_export= True
    column_labels = dict(tenthuoc="Tên thuốc", soluong="Số lượng", dongia="Đơn giá", trangthai="Trạng thái", o_tencachdung="Cách dùng", o_tendonvi="Đơn vị")
    column_searchable_list = ("tenthuoc", "dongia")
    page_size = 10   #phân trang

class DonViModelView(ModelView):
    column_labels = dict(tendonvi="Đơn vị thuốc")
    page_size = 10   #phân trang

class CachDungModelView(ModelView):
    column_labels = dict(tencachdung="Cách dùng thuốc")
    page_size = 10   #phân trang

class QuyDinhModelView(ModelView):
    column_labels = dict(tenquydinh="Tên quy định", quydinh="Quy định")
    page_size = 10   #phân trang

class LogoutView(BaseView):
    @expose("/")
    def index(seft):
        session.clear()
        return redirect(url_for('user.user_login'))

admin.add_view(ThuocModelView(Thuoc, db.session, name="Thuốc"))
admin.add_view(DonViModelView(DonVi, db.session, name="Đơn vị"))
admin.add_view(CachDungModelView(CachDung, db.session, name="Cách dùng"))
admin.add_view(QuyDinhModelView(QuyDinh, db.session, name="Quy định khác"))
admin.add_view(LogoutView(name="Đăng xuất"))

