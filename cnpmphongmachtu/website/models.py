# Import các thư viện cần thiết
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from website import db
from sqlalchemy.orm import relationship
from datetime import datetime
from flask_login import UserMixin

# ----------------------- Tạo class ----------------


class QuyDinh(db.Model):
    __tablename__ = "QuyDinh"
    maquydinh = db.Column(db.Integer, primary_key=True)
    tenquydinh = db.Column(db.String(300), nullable=False)
    quydinh = db.Column(db.Float, nullable=False)


class Quyen(db.Model):
    __tablename__ = "Quyen"
    maquyen = db.Column(db.Integer, primary_key=True)
    tenquyen = db.Column(db.String(300), nullable=False)
    taikhoans = db.relationship("TaiKhoan", backref="o_quyen", lazy=False)


class TaiKhoan(db.Model, UserMixin):
    __tablename__ = "TaiKhoan"
    madangnhap = db.Column(db.Integer, autoincrement=True, primary_key=True)
    tendangnhap = db.Column(db.String(150), unique=True)
    matkhau = db.Column(db.String(150), nullable=False)
    ma_quyen = db.Column(db.Integer, db.ForeignKey(Quyen.maquyen), unique=True)


class DanhSachKham(db.Model):
    __tablename__ = "DanhSachKham"
    mads = db.Column(db.Integer, autoincrement=True, primary_key=True)
    ngaykham = db.Column(db.Date, default=datetime.now().date())
    hoten = db.Column(db.String(300), nullable=False)
    gioitinh = db.Column(db.Integer, nullable=False)
    namsinh = db.Column(db.String(300), nullable=False)
    diachi = db.Column(db.String(300), nullable=False)
    cmnd = db.Column(db.String(300), nullable=False)
    sdt = db.Column(db.String(300), nullable=False)
    trangthai = db.Column(db.Boolean, nullable=False)


class BenhNhan(db.Model):
    __tablename__ = "BenhNhan"
    mabn = db.Column(db.Integer, autoincrement=True, primary_key=True)
    hoten = db.Column(db.String(300), nullable=False)
    gioitinh = db.Column(db.Integer, nullable=False)
    namsinh = db.Column(db.String(300), nullable=False)
    diachi = db.Column(db.String(300), nullable=False)
    cmnd = db.Column(db.String(300), unique=True, nullable=False)
    sdt = db.Column(db.String(300), nullable=False)
    phieukhams = relationship("PhieuKham", backref="o_benhnhan", lazy=False)


class PhieuKham(db.Model):
    __tablename__ = "PhieuKham"
    mapk = db.Column(db.Integer, autoincrement=True, primary_key=True)
    ngaykham = db.Column(db.Date, default=datetime.now().date())
    trieuchung = db.Column(db.String(300), nullable=False)
    loaibenh = db.Column(db.String(300), nullable=False)
    tienkham = db.Column(db.Float, default=0)
    ma_bn = db.Column(db.Integer, db.ForeignKey(BenhNhan.mabn), nullable=False)
    toathuocs = relationship("ToaThuoc", backref="o_phieukham", lazy=False)
    hoadons = relationship("HoaDon", backref="o_phieukham", lazy=False)


class ToaThuoc(db.Model):
    __tablename__ = "ToaThuoc"
    matoa = db.Column(db.Integer, autoincrement=True, primary_key=True)
    ngayke = db.Column(db.Date, default=datetime.now().date())
    tienthuoc = db.Column(db.Float, default=0)
    ma_pk = db.Column(db.Integer, db.ForeignKey(PhieuKham.mapk), unique=True)
    hoadons = relationship("HoaDon", backref="o_toathuoc", lazy=False)
    chitiettoas = relationship("ChiTietToa", backref="o_toathuoc", lazy=False)


class HoaDon(db.Model):
    __tablename__ = "HoaDon"
    mahd = db.Column(db.Integer, autoincrement=True, primary_key=True)
    ngayban = db.Column(db.Date, default=datetime.now().date())
    tongthu = db.Column(db.Float, default=0)
    dathanhtoan = db.Column(db.Boolean, default=False)
    ma_pk = db.Column(db.Integer, db.ForeignKey(PhieuKham.mapk), unique=True)
    ma_toa = db.Column(db.Integer, db.ForeignKey(ToaThuoc.matoa), unique=True)


class CachDung(db.Model):
    __tablename__ = "CachDung"
    macachdung = db.Column(db.Integer, autoincrement=True, primary_key=True)
    tencachdung = db.Column(db.String(300), nullable=False)
    thuocs = relationship("Thuoc", backref="o_tencachdung", lazy=True)

    def __str__(seft):
        return seft.tencachdung


class DonVi(db.Model):
    __tablename__ = "DonVi"
    madonvi = db.Column(db.Integer, autoincrement=True, primary_key=True)
    tendonvi = db.Column(db.String(300), nullable=False)
    thuocs = relationship("Thuoc", backref="o_tendonvi", lazy=True)

    def __str__(seft):
        return seft.tendonvi


class Thuoc(db.Model):
    __tablename__ = "Thuoc"
    mathuoc = db.Column(db.Integer, autoincrement=True, primary_key=True)
    tenthuoc = db.Column(db.String(300), unique=True, nullable=False)
    soluong = db.Column(db.Integer, default=0)
    dongia = db.Column(db.Float, default=0)
    madonvi = db.Column(db.Integer, db.ForeignKey(DonVi.madonvi), unique=False)
    macachdung = db.Column(db.Integer,
                           db.ForeignKey(CachDung.macachdung),
                           unique=False)
    trangthai = db.Column(db.Integer, default=1)


class ChiTietToa(db.Model):
    __tablename__ = "ChiTietToa"
    matoa = db.Column(db.Integer,
                      db.ForeignKey(ToaThuoc.matoa),
                      primary_key=True)
    mathuoc = db.Column(db.Integer,
                        db.ForeignKey(Thuoc.mathuoc),
                        primary_key=True)
    soluong = db.Column(db.Integer, default=0)
    tienthuoc = db.Column(db.Float, default=0)
    thuocs = db.relationship("Thuoc", backref="o_chitiettoa", lazy=False)


if __name__ == "__main__":
    # Xoá database
    #db.drop_all()
    # Tạo database
    #db.create_all()
    q1 = Quyen(maquyen=1, tenquyen="Admin")
    q2 = Quyen(maquyen=2, tenquyen="Bác sĩ")
    q3 = Quyen(maquyen=3, tenquyen="Y tá")
    q4 = Quyen(maquyen=4, tenquyen="Khách hàng")
    db.session.add(q1)
    db.session.add(q2)
    db.session.add(q3)
    db.session.add(q4)
    tk1 = TaiKhoan(tendangnhap="admin", matkhau="123", ma_quyen=1)
    tk2 = TaiKhoan(tendangnhap="bacsi", matkhau="123", ma_quyen=2)
    tk3 = TaiKhoan(tendangnhap="yta", matkhau="123", ma_quyen=3)
    tk4 = TaiKhoan(tendangnhap="user", matkhau="123", ma_quyen=4)
    db.session.add(tk1)
    db.session.add(tk2)
    db.session.add(tk3)
    db.session.add(tk4)
    qd1 = QuyDinh(maquydinh=1, tenquydinh="Số khách hàng tối đa", quydinh=40)
    qd2 = QuyDinh(maquydinh=2, tenquydinh="Tiền khám", quydinh=80000)
    db.session.add(qd1)
    db.session.add(qd2)
    dv1 = DonVi(tendonvi="Viên nén")
    dv2 = DonVi(tendonvi="Hủ")
    dv3 = DonVi(tendonvi="Vỉ")
    db.session.add(dv1)
    db.session.add(dv2)
    db.session.add(dv3)
    cd1 = CachDung(tencachdung="Uống")
    cd2 = CachDung(tencachdung="Ngậm")
    db.session.add(cd1)
    db.session.add(cd2)
    db.session.commit()
