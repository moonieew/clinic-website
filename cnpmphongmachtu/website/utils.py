# Import các thư viện cần thiết
import sys
import os

from flask_login.utils import login_user

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from website.models import BenhNhan, DanhSachKham, TaiKhoan, PhieuKham, ToaThuoc, Thuoc, ChiTietToa, HoaDon, CachDung, DonVi, QuyDinh
from datetime import datetime, timedelta
from website import db
from sqlalchemy.sql import func
from sqlalchemy import desc

#Xử lí một số vấn đề về thời gian
# Lấy thời gian ngày hôm nay [ngày và giờ hiện tại]
today = datetime.today().date()
yesterday = today - timedelta(days=1)
tomorrow = today + timedelta(days=1)


# Xử lí các chức năng CRUD
# --------------------TÀI KHOẢN---------------------
# Lấy tất cả tài khoản
def get_taikhoan_all():
    return TaiKhoan.query.all()


# Lấy tài khoản theo lúc đăng nhập
def get_login(username, password):
    return TaiKhoan.query.filter(TaiKhoan.tendangnhap == username,
                                 TaiKhoan.matkhau == password).first()


# Lấy tài khoản theo tên tài khoản
def get_taikhoan_by_usernames(usernames):
    return TaiKhoan.query.filter(TaiKhoan.tendangnhap == usernames).first()


# --------------------BỆNH NHÂN---------------------
# Lấy toàn bộ danh sách bệnh nhân (phân trang)
def get_benhnhan_all(current_page=None, per_page=None):
    return BenhNhan.query.paginate(page=current_page, per_page=per_page)


# Lấy 1 bệnh nhân theo cmnd :
def get_benhnhan_by_cmnd(cmnd):
    return BenhNhan.query.filter(BenhNhan.cmnd == cmnd).first()


# Lấy 1 bệnh nhân theo mã bệnh nhân :
def get_benhnhan_by_mabn(mabn):
    return BenhNhan.query.filter(BenhNhan.mabn == mabn).first()


# --------------------PHIẾU KHÁM--------------------
# Lấy 1 phiếu khám theo mã phiếu khám
def get_pk_by_mapk(mapk):
    return PhieuKham.query.filter(PhieuKham.mapk == mapk).first()


# Lấy toàn bộ phiếu khám theo mã bệnh nhân (có phân trang)
def get_pk_all_by_mabn(mabn, current_page=None, per_page=None):
    return PhieuKham.query.filter(PhieuKham.ma_bn == mabn).paginate(
        page=current_page, per_page=per_page)


# Lấy phiếu khám + bệnh nhân + toa thuốc chưa lập hoá đơn
def get_pk_no_hd(current_page=None, per_page=None):
    return db.session.query(
        PhieuKham.mapk, ToaThuoc.matoa, BenhNhan.mabn, BenhNhan.hoten,
        PhieuKham.ngaykham, PhieuKham.trieuchung, PhieuKham.loaibenh,
        PhieuKham.tienkham,
        ToaThuoc.tienthuoc).select_from(PhieuKham).join(ToaThuoc).join(
            BenhNhan).filter(PhieuKham.hoadons == None).paginate(
                page=current_page, per_page=per_page)


# --------------------TOA THUỐC---------------------
# Lấy toa thuốc theo mã toa thuốc
def get_toathuoc_by_matoa(matoa):
    return ToaThuoc.query.filter(ToaThuoc.matoa == matoa).first()


# Lấy toa thuốc theo mã phiếu khám
def get_toathuoc_by_mapk(mapk):
    return ToaThuoc.query.filter(ToaThuoc.ma_pk == mapk).first()


# ----------------CHI TIẾT TOA THUỐC----------------
# Lấy tất cả chi tiết thuốc theo mã toa
def get_chitiettoa_by_matoa(ma_toa):
    return db.session.query(
        Thuoc.tenthuoc, ChiTietToa.soluong, CachDung.tencachdung,
        ChiTietToa.tienthuoc, ToaThuoc.matoa,
        Thuoc.mathuoc).select_from(ChiTietToa).join(ToaThuoc).join(Thuoc).join(
            CachDung).filter(ToaThuoc.matoa == ma_toa).all()


# Lấy chi tiết thuốc theo mã toa và mã thuốc
def get_chitiet_by_matoa_mathuoc(matoa, mathuoc):
    return ChiTietToa.query.filter(ChiTietToa.matoa == matoa).filter(
        ChiTietToa.mathuoc == mathuoc).first()


# Lấy tất cả chi tiết thuốc theo mã hoá đơn
def get_chitiet_by_mahd(mahd):
    return db.session.query(
        Thuoc.tenthuoc, ChiTietToa.soluong, DonVi.tendonvi,
        ChiTietToa.tienthuoc).select_from(HoaDon).join(ToaThuoc).join(
            ChiTietToa).join(Thuoc).join(DonVi).filter(
                HoaDon.mahd == mahd).all()


# ---------------------THUỐC------------------------
def get_thuoc_all():
    return Thuoc.query.all()


def get_thuoc_by_mathuoc(mathuoc):
    return Thuoc.query.filter(Thuoc.mathuoc == mathuoc).first()


def get_thuoc_all_dv():
    return db.session.query(
        Thuoc, DonVi).join(DonVi).filter(Thuoc.trangthai == 1).all()


# ---------------------HOÁ ĐƠN----------------------
# Lấy hoá đơn theo mã hoá đơn
def get_hoadon_by_mahd(mahd):
    return HoaDon.query.filter(HoaDon.mahd == mahd).first()


# Lấy toàn bộ hoá đơn có (tiền thuốc + tiền khám) (có phân trang)
def get_hoadon(current_page=None, per_page=None):
    return db.session.query(
        HoaDon.mahd, HoaDon.ngayban, PhieuKham.tienkham, ToaThuoc.tienthuoc,
        HoaDon.tongthu, HoaDon.dathanhtoan).select_from(
            HoaDon).join(PhieuKham).join(ToaThuoc).order_by(
                desc(HoaDon.ngayban)).paginate(page=current_page,
                                               per_page=per_page)


# Lấy chi tiết hoá đơn, bao gồm thông tin bệnh nhân, chi tiết thuốc theo mã hoá đơn
def get_cthoadon_by_mahd(mahd):
    return db.session.query(
        HoaDon.mahd, BenhNhan.hoten, HoaDon.ngayban, PhieuKham.tienkham,
        ToaThuoc.tienthuoc,
        HoaDon.tongthu).select_from(ToaThuoc).join(HoaDon).join(
            PhieuKham).join(BenhNhan).filter(HoaDon.mahd == mahd).filter(
                HoaDon.dathanhtoan == True).first()


# Lấy báo cáo doanh thu
def get_baocao(current_page=None,
               per_page=None,
               firstDate=None,
               lastDate=None):
    return db.session.query(
        HoaDon.ngayban,
        func.count(HoaDon.ma_pk).label("tong_bn"),
        func.sum(
            HoaDon.tongthu).label("doanh_thu")).select_from(HoaDon).filter(
                HoaDon.ngayban.between(firstDate, lastDate)).group_by(
                    HoaDon.ngayban).paginate(page=current_page,
                                             per_page=per_page)


# -----------------DANH SÁCH KHÁM-------------------
#Lấy bệnh nhân trong ds khám theo cmnd
def get_ds_by_cmnd(cmnd):
    return DanhSachKham.query.filter(DanhSachKham.cmnd == cmnd).first()


# Lấy toàn bộ danh sách khám có phân trang
def get_ds_all(current_page=None, per_page=None):
    return DanhSachKham.query.paginate(page=current_page, per_page=per_page)


# Lấy danh sách khám theo ngày hôm nay
def get_ds_today(current_page=None, per_page=None):
    return DanhSachKham.query.filter(
        DanhSachKham.ngaykham.between(today, tomorrow)).filter(
            DanhSachKham.trangthai == False).paginate(page=current_page,
                                                      per_page=per_page)


# Đếm danh sách kham theo ngày hôm nay
def count_dskham_today():
    obj = db.session.query(func.count(
        DanhSachKham.mads).label("slkham")).select_from(DanhSachKham).filter(
            DanhSachKham.ngaykham.between(today, tomorrow)).first()
    return obj


# -----------------QUY ĐỊNH-------------------
def get_max_dskham():
    return QuyDinh.query.filter(QuyDinh.maquydinh == 1).first()


if __name__ == '__main__':
    tienkham = get_ds_by_cmnd(1234)
    print(tienkham.trangthai)
