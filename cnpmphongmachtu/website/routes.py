import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from website import app, db, utils, login
from website.models import BenhNhan, DanhSachKham, TaiKhoan, PhieuKham, ToaThuoc, Thuoc, ChiTietToa, HoaDon
import calendar
import datetime
from website import utils
from website.admin import *
from flask_login import login_user
# Tạo tên các prefix
yta = Blueprint('yta', __name__)
user = Blueprint('user', __name__)
bacsi = Blueprint('bacsi', __name__)

# Xử lí các trang
#--------------------NGƯỜI DÙNG---------------------

# Chặn người dùng đăng nhập trái phép
# Dùng @login_required chèn giữa @exam.route('/...') và hàm để chặn


def login_admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session and session['maquyen'] == 1:
            return f(*args, **kwargs)
        else:
            session.clear()
            return redirect(url_for('user.user_login'))

    return wrap


def login_bacsi_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session and session['maquyen'] == 2:
            return f(*args, **kwargs)
        else:
            session.clear()
            return redirect(url_for('user.user_login'))

    return wrap


def login_yta_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session and session['maquyen'] == 3:
            return f(*args, **kwargs)
        else:
            session.clear()
            return redirect(url_for('user.user_login'))

    return wrap


def login_user_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session and session['maquyen'] == 4:
            return f(*args, **kwargs)
        else:
            session.clear()
            return redirect(url_for('user.user_login'))

    return wrap


# Trang khách đặt lịch khám
@user.route('/', methods=['GET', 'POST'])
@user.route('/home', methods=['GET', 'POST'])
@login_user_required
def user_home():
    if request.method == 'POST':
        ngaykham = utils.today
        hoten = request.form.get("hoten")
        gioitinh = request.form.get("gioitinh")
        namsinh = request.form.get("namsinh")
        cmnd = request.form.get("cmnd")
        diachi = request.form.get("diachi")
        sdt = request.form.get("sdt")
        trangthai = False
        nguoikham = DanhSachKham(ngaykham=ngaykham,
                                 hoten=hoten,
                                 gioitinh=gioitinh,
                                 namsinh=namsinh,
                                 cmnd=cmnd,
                                 diachi=diachi,
                                 sdt=sdt,
                                 trangthai=trangthai)

        gioiHanKham = utils.get_max_dskham()
        dem = utils.count_dskham_today()
        if (dem[0] <= int(gioiHanKham.quydinh)):
            try:
                db.session.add(nguoikham)

                db.session.commit()
                flash("Bạn đã đặt lịch khám thành công", "success")
            except:
                flash("Bạn đã đặt lịch khám thất bại", "error")
        else:
            flash("Quy phạm quy định", "error")
            print("Quy phạm quy định")
    return render_template('user_home.html')


# Trang đăng nhập
@user.route('/login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        session.pop('user', None)
        tentaikhoan = request.form['username']
        matkhau = request.form['password']
        dangnhap = utils.get_login(tentaikhoan, matkhau)
        if dangnhap == None:
            flash("Tên đăng nhập hoặc mật khẩu không đúng", "error")
        else:
            #Tạo session
            session["maquyen"] = dangnhap.ma_quyen
            session["logged_in"] = True
            #Phân quyền với 1 - Admin, 2 - Bác sĩ, 3 - Y tá, 4 - Người dùng
            if (session["maquyen"] == 1):
                '''Nếu bị lỗi không tìm thấy id
                   Vào models bấm ctrl + chuột trái vào UserMixin
                   Tìm hàm def get_id(self):
                   Sửa dòng return text_type(self.id) thành return text_type(self.madangnhap)'''
                login_user(dangnhap)
                return redirect("/admin")
            if (session["maquyen"] == 2):
                return redirect(url_for("bacsi.bacsi_danhsachkham"))
            if (session["maquyen"] == 3):
                return redirect(url_for("yta.yta_danhsachkham"))
            if (session["maquyen"] == 4):
                return redirect(url_for("user.user_home"))
    return render_template('login.html')


# Xử lí logout
@user.route('/logout')
def user_logout():
    session.clear()
    return redirect(url_for('user.user_login'))


# Trang đăng kí tài khoản
@user.route('/register', methods=['GET', 'POST'])
def user_register():
    if request.method == 'POST':
        session.pop('user', None)
        tentaikhoan = request.form['username']
        matkhau = request.form['password']
        matkhau_nhaplai = request.form['repassword']
        print(tentaikhoan)
        print(matkhau_nhaplai)
        print(matkhau)
        dangnhap = utils.get_taikhoan_by_usernames(tentaikhoan)
        if (dangnhap is None):
            if (matkhau == matkhau_nhaplai):
                taiKhoanMoi = TaiKhoan(tendangnhap=tentaikhoan,
                                       matkhau=matkhau,
                                       maquyen=3)
                db.session.add(taiKhoanMoi)
                db.session.commit()
                flash("Tạo tài khoản thành công", "success")
            else:
                flash("Mật khẩu nhập lại phải trùng khớp", "error")
        else:
            flash("Tài khoản đã tồn tại", "error")
    return render_template('register.html')


#--------------------Y TÁ---------------------


# Trang hoá đơn
@yta.route('/hoadon', methods=['GET', 'POST'])
@login_yta_required
def yta_hoadon():
    # Phân trang cho những Phiếu khám chưa lập thành hoá đơn
    current_pageTop = request.args.get('pageTop', 1, type=int)
    # Phân trang cho những Hoá Đơn chưa thanh toán
    current_pageBot = request.args.get('pageBot', 1, type=int)
    # Gọi danh sách phiếu khám chưa lập hoá đơn
    dsphieukham_no_hd = utils.get_pk_no_hd(current_pageTop, 4)
    # Gọi danh sách Hoá Đơn chưa thanh toán
    dshoadon = utils.get_hoadon(current_pageBot, 4)
    return render_template('yta_hoadon.html',
                           dsphieukham=dsphieukham_no_hd,
                           dshoadon=dshoadon)


# Lập hoá đơn
@yta.route('/laphoadon', methods=['GET', 'POST'])
@login_yta_required
def yta_laphoadon():
    mapk = request.args.get("mapk")
    phieukham = utils.get_pk_by_mapk(mapk)
    toathuocs = utils.get_toathuoc_by_mapk(mapk)
    ngayban = utils.today
    try:
        hoadon = HoaDon(ngayban=ngayban, dathanhtoan=False)
        phieukham.hoadons.append(hoadon)
        toathuocs.hoadons.append(hoadon)
        hoadon.tongthu = phieukham.tienkham + toathuocs.tienthuoc
        db.session.commit()
        print("Lập hoá đơn thành công")
        return redirect(url_for("yta.yta_hoadon"))
    except:
        print("Lập hoá đon thất bại")
        return redirect(url_for("yta.yta_hoadon"))


# Chi tiết hoá đơn
@yta.route('/chitiethoadon', methods=['GET', 'POST'])
@login_yta_required
def yta_chitiethoadon():
    mahd = request.args.get('mahd')
    chitiet_thongtin = utils.get_cthoadon_by_mahd(mahd)
    chitiet_thuoc = utils.get_chitiet_by_mahd(mahd)
    return render_template('yta_chitiethoadon.html',
                           dsthongtin=chitiet_thongtin,
                           dschitiet=chitiet_thuoc)


# Thanh toán hoá đơn
@yta.route('/thanhtoanhoadon', methods=['GET', 'POST'])
@login_yta_required
def yta_thanhtoanhoadon():
    mahd = request.args.get("mahd")
    hoadon = utils.get_hoadon_by_mahd(mahd)
    try:
        print("Chỉnh")
        print(hoadon)
        hoadon.dathanhtoan = True
        print("Chuẩn bị commit")
        db.session.commit()
        print("Đã thanh toán thành công")
        return redirect(url_for("yta.yta_hoadon"))
    except:
        print("Thanh toán thất bại")
        return redirect(url_for("yta.yta_hoadon"))


#CRUD Danh sách khám
#Thêm bệnh nhân khám
@yta.route('/themdskham', methods=['POST', 'GET'])
@login_yta_required
def yta_themdskham():
    if request.method == 'POST':
        ngaykham = utils.today
        hoten = request.form.get("hoten")
        gioitinh = request.form.get("gioitinh")
        namsinh = request.form.get("namsinh")
        cmnd = request.form.get("cmnd")
        diachi = request.form.get("diachi")
        sdt = request.form.get("sdt")
        trangthai = False
        nguoikham = DanhSachKham(ngaykham=ngaykham,
                                 hoten=hoten,
                                 gioitinh=gioitinh,
                                 namsinh=namsinh,
                                 cmnd=cmnd,
                                 diachi=diachi,
                                 sdt=sdt,
                                 trangthai=trangthai)
        gioiHanKham = utils.get_max_dskham()
        dem = utils.count_dskham_today()
        if (dem[0] <= int(gioiHanKham.quydinh)):
            try:

                db.session.add(nguoikham)
                db.session.commit()
                print("Thêm thành công")
                return redirect(url_for("yta.yta_themdskham"))
            except:
                print("Thêm thất bại")
        else:
            print("Quy phạm quy định")
    return render_template('yta_themdskham.html')


# Xoá bệnh nhân trong danh sách khám
@yta.route('/xoa-danhsachkham', methods=['GET', 'POST'])
@login_yta_required
def yta_xoadanhsachkham():
    mads = request.args.get('mads')
    nguoikham = DanhSachKham.query.filter(DanhSachKham.mads == mads).first()
    print("Mã danh sách lấy được : " + "'" + str(id) + "'")
    print(nguoikham)
    try:
        db.session.delete(nguoikham)
        db.session.commit()
        print("Xoá thành công")
        #redirect thì truyền tên hàm phía dưới route theo cú pháp <blueprint-name>.<tên hàm>
        return redirect(url_for("yta.yta_danhsachkham"))
    except:
        print("Xoá thất bại")
    return redirect(url_for("yta.yta_danhsachkham"))


# Danh sách bệnh nhân khám ngày hôm nay
@yta.route('/')
@yta.route('/danhsachkham')
@login_yta_required
def yta_danhsachkham():
    current_page = request.args.get('page', 1, type=int)
    danhsachkham = utils.get_ds_today(current_page, 5)
    return render_template('yta_danhsachkham.html', danhsach=danhsachkham)


# Trang báo cáo doanh thu theo ngày
@yta.route('/baocao', methods=['GET', 'POST'])
@login_yta_required
def yta_baocao():
    current_page = request.args.get('page', 1, type=int)
    today = utils.today
    fdate_of_month = today.replace(day=1)
    ldate_of_month = today.replace(
        day=calendar.monthrange(today.year, today.month)[1])

    danhsachbc = utils.get_baocao(current_page,
                                  5,
                                  firstDate=fdate_of_month,
                                  lastDate=ldate_of_month)
    if request.method == 'POST':
        # Lấy ngày từ trên form về
        ngaydau = request.form.get('ngaydau')
        ngaycuoi = request.form.get('ngaycuoi')
        try:
            danhsachbc = utils.get_baocao(current_page,
                                          5,
                                          firstDate=ngaydau,
                                          lastDate=ngaycuoi)
            return render_template('yta_baocao.html',
                                   danhsach=danhsachbc,
                                   fdate=fdate_of_month,
                                   ldate=ldate_of_month)
        except:
            print("Không lấy được ngày")
    return render_template('yta_baocao.html',
                           danhsach=danhsachbc,
                           fdate=fdate_of_month,
                           ldate=ldate_of_month)


#Thêm người
#--------------------BÁC SĨ--------------------


#Xem tất cả bệnh nhân trong danh sách khám
@bacsi.route('/')
@bacsi.route('/danhsachkham')
@login_bacsi_required
def bacsi_danhsachkham():
    current_page = request.args.get('page', 1, type=int)
    danhsachkham = utils.get_ds_today(current_page, 5)
    return render_template('bacsi_danhsachkham.html', danhsach=danhsachkham)


#Danh sách bệnh nhân
@bacsi.route('/danhsachbenhnhan')
@login_bacsi_required
def bacsi_danhsachbenhnhan():
    current_page = request.args.get('page', 1, type=int)
    danhsach = utils.get_benhnhan_all(current_page, 5)
    return render_template('bacsi_danhsachbenhnhan.html', danhsach=danhsach)


#Thêm bệnh nhân nếu bệnh nhân chưa có trong Danh sách
@bacsi.route('/thembenhnhan', methods=['GET', 'POST'])
@login_bacsi_required
def bacsi_thembenhnhan():
    cmnd = request.args.get('cmnd', 123, type=str)
    benhnhan = utils.get_benhnhan_by_cmnd(cmnd)
    benhNhan_dskham = utils.get_ds_by_cmnd(cmnd)
    # Nếu chưa có bệnh nhân nào thì thêm bệnh nhân trong ds khám vào thành bệnh nhân mới
    if benhnhan == None:
        hoten = benhNhan_dskham.hoten
        namsinh = benhNhan_dskham.namsinh
        gioitinh = benhNhan_dskham.gioitinh
        diachi = benhNhan_dskham.diachi
        cmnd = benhNhan_dskham.cmnd
        sdt = benhNhan_dskham.sdt
        benhNhanMoi = BenhNhan(hoten=hoten,
                               gioitinh=gioitinh,
                               namsinh=namsinh,
                               diachi=diachi,
                               cmnd=cmnd,
                               sdt=sdt)
        try:
            db.session.add(benhNhanMoi)
            benhNhan_dskham.trangthai = True
            db.session.commit()
            print("Thêm thành công")
            # Thêm xong đẩy qua trang lập phiếu khám
            return redirect(url_for('bacsi.bacsi_lapphieukham', cmnd=cmnd))
        except:
            print("Thêm thất bại")
    # Nếu có rồi thì chỉ đẩy cmnd qua thẳng lập phiếu khám luôn
    else:
        benhNhan_dskham.trangthai = True
        db.session.commit()
        return redirect(url_for('bacsi.bacsi_lapphieukham', cmnd=cmnd))


# Xoá bệnh nhân trong danh sách khám
@bacsi.route('/xoa-danhsachkham', methods=['GET', 'POST'])
@login_bacsi_required
def bacsi_xoadanhsachkham():
    mads = request.args.get('mads')
    danhsachkham = DanhSachKham.query.filter(DanhSachKham.mads == mads).first()
    try:
        db.session.delete(danhsachkham)
        db.session.commit()
        print("Xoá thành công")
        return redirect(url_for("bacsi.bacsi_danhsachkham"))
    except:
        print("Xoá thất bại")
    return redirect(url_for("bacsi.bacsi_danhsachkham"))


#Xóa bệnh nhân trong bảng bệnh nhân
@bacsi.route('/xoa-benhnhan', methods=['GET', 'POST'])
@login_bacsi_required
def bacsi_xoabenhnhan():
    mabn = request.args.get('mabn')
    benhnhan = BenhNhan.query.filter(BenhNhan.mabn == mabn).first()
    print(benhnhan)
    try:
        db.session.delete(benhnhan)
        db.session.commit()
        print("Xoá thành công")
        return redirect(url_for("bacsi.bacsi_danhsachbenhnhan"))
    except:
        print("Xoá thất bại")

    return redirect(url_for("bacsi.bacsi_danhsachbenhnhan"))


# Thêm thuốc cho bệnh nhân trong phiếu khám
@bacsi.route("/themtoathuoc", methods=['GET', 'POST'])
@login_bacsi_required
def bacsi_them_thuocpk():
    # Lấy mã toa từ trang lập phiếu khám qua
    matoa = request.args.get('matoa', 123, type=str)
    ngayke = utils.today
    chiTietToa = utils.get_chitiettoa_by_matoa(matoa)
    thuocs = utils.get_thuoc_all_dv()
    if request.method == 'POST':
        matoa = request.form.get('matoa')
        mathuoc = request.form.get('mathuoc')
        soluong = request.form.get('soluong')
        toathuoc = utils.get_toathuoc_by_matoa(matoa)
        thuoc_obj = utils.get_thuoc_by_mathuoc(mathuoc)
        # Lấy chi tiết toa thuốc của toa thuốc hiện tại
        ct = toathuoc.chitiettoas
        if request.form['themthuoc'] == "Thêm thuốc":
            # Kiểm tra trong chi tiết toa này có thuốc đó hay Chưa
            exist = utils.get_chitiet_by_matoa_mathuoc(matoa, mathuoc)
            try:
                if exist is None:
                    if (thuoc_obj.soluong < int(soluong)):
                        soluong = thuoc_obj.soluong
                        thuoc_obj.soluong = 0
                        thuoc_obj.trangthai = 0
                    else:
                        thuoc_obj.soluong -= int(soluong)
                    toathuoc.chitiettoas.append(
                        ChiTietToa(soluong=soluong,
                                   tienthuoc=thuoc_obj.dongia,
                                   thuocs=thuoc_obj))
                    # Cập nhật giá cho toa thuốc (vì mới thêm thuốc vào)
                    db.session.commit()
                    print("Thêm chi tiết thuốc thành công")
                    # Cập nhật lại giá tiền cho toa thuốc
                    toathuoc.tienthuoc = 0
                    for cts in ct:
                        toathuoc.tienthuoc += cts.soluong * cts.tienthuoc  # Cộng lại
                    db.session.commit()
                    print("Cập nhật tiền trong toa thuốc thành công")
                    return redirect(
                        url_for('bacsi.bacsi_them_thuocpk', matoa=matoa))
                # Nếu có rồi thì lấy cập nhật số lượng lên
                else:
                    exist.soluong = exist.soluong + int(soluong)
                    # Cập nhật lại số lượng
                    db.session.commit()
                    print("Cập nhật số lượng thành công")
                    # Cập nhật lại tiền có trong toa thuốc
                    # Reset tiền
                    toathuoc.tienthuoc = 0
                    for cts in ct:
                        toathuoc.tienthuoc += cts.soluong * cts.tienthuoc  # Cộng lại
                    db.session.commit()
                    print("Cập nhật tiền trong toa thuốc thành công")
                    return redirect(
                        url_for('bacsi.bacsi_them_thuocpk', matoa=matoa))
            except:
                print("Thêm chi tiết thuốc thất bại")

    return render_template('bacsi_themthuoc.html',
                           dsthuoc=thuocs,
                           dschitiet=chiTietToa,
                           danhsach=0,
                           matoa=matoa,
                           ngayke=ngayke)


# Xoá chi tiết thuốc có trong giỏ
@bacsi.route("/xoa-chitietthuoc")
@login_bacsi_required
def bacsi_xoachitietthuoc():
    matoa = request.args.get('matoa')
    mathuoc = request.args.get('mathuoc')
    delete_obj = utils.get_chitiet_by_matoa_mathuoc(matoa, mathuoc)
    thuoc_obj = utils.get_thuoc_by_mathuoc(mathuoc)
    if (delete_obj != None):
        soluong = delete_obj.soluong
        thuoc_obj.soluong += soluong
        if (thuoc_obj.trangthai == 0):
            thuoc_obj.trangthai = 1
        db.session.delete(delete_obj)
        db.session.commit()
        # Cập nhật lại tiền trong toa thuốc
        toathuoc = utils.get_toathuoc_by_matoa(matoa)
        ct = toathuoc.chitiettoas
        toathuoc.tienthuoc = 0
        for cts in ct:
            toathuoc.tienthuoc += cts.tienthuoc * cts.soluong
        db.session.commit()
        return redirect(url_for('bacsi.bacsi_them_thuocpk', matoa=matoa))


# Lập phiếu khám cho bệnh nhân
@bacsi.route('/lapphieukham', methods=['GET', 'POST'])
@login_bacsi_required
def bacsi_lapphieukham():
    cmnd = request.args.get('cmnd', 123, type=str)
    benhnhan = utils.get_benhnhan_by_cmnd(cmnd)
    mabn = -1
    tenbenhnhan = "Không có"
    if benhnhan is not None:
        tenbenhnhan = benhnhan.hoten
        mabn = benhnhan.mabn
    ngaykham = utils.today
    tienkham_set = QuyDinh.query.filter(QuyDinh.maquydinh == 2).first().quydinh
    if request.method == 'POST':
        mabn = request.form.get('mabn')
        benhnhan = utils.get_benhnhan_by_mabn(mabn)
        trieuchung = request.form.get('trieuchung')
        loaibenh = request.form.get('loaibenh')
        tienkham = float(request.form.get('tienkham'))
        phieukham = PhieuKham(trieuchung=trieuchung,
                              ngaykham=ngaykham,
                              loaibenh=loaibenh,
                              tienkham=tienkham)
        if request.form['ketoa'] == "Kê toa":
            try:
                benhnhan.phieukhams.append(phieukham)
                db.session.add(phieukham)
                db.session.commit()
                print("Tạo phiếu khám thành công")
                mapk = phieukham.mapk
                toathuocs = ToaThuoc(ma_pk=mapk)
                phieukham.toathuocs.append(toathuocs)
                db.session.commit()
                matoa = toathuocs.matoa
                print("Tạo toa thuốc thành công")
                return redirect(
                    url_for('bacsi.bacsi_them_thuocpk', matoa=matoa))
            except:
                print("Kê toa thất bại")
        elif request.form['thanhtoan'] == "Khám xong":
            try:
                benhnhan.phieukhams.append(phieukham)
                db.session.add(phieukham)
                db.session.commit()
                print("Tạo phiếu khám thành công")
                return redirect(url_for('bacsi.bacsi_danhsachkham'))
            except:
                print("Chuyển hướng thất bại")
        else:
            print("Thêm thất bại")

    return render_template('bacsi_lapphieukham.html',
                           ngaykham=ngaykham,
                           mabn=mabn,
                           tenbenhnhan=tenbenhnhan,
                           tienkham_set=tienkham_set)


@bacsi.route('/lichsukham')
@login_bacsi_required
def bacsi_lichsukham():
    mabn = request.args.get('mabn')
    current_page = request.args.get('page', 1, type=int)
    dsbenhnhan = utils.get_benhnhan_by_mabn(mabn)
    dsphieukham = utils.get_pk_all_by_mabn(mabn, current_page, 5)
    return render_template('bacsi_lichsukham.html',
                           dsthongtin=dsbenhnhan,
                           dschitiet=dsphieukham)


# Trang báo cáo doanh thu theo ngày
@bacsi.route('/baocao', methods=['GET', 'POST'])
@login_bacsi_required
def bacsi_baocao():
    current_page = request.args.get('page', 1, type=int)
    today = utils.today
    fdate_of_month = today.replace(day=1)
    ldate_of_month = today.replace(
        day=calendar.monthrange(today.year, today.month)[1])

    danhsachbc = utils.get_baocao(current_page,
                                  5,
                                  firstDate=fdate_of_month,
                                  lastDate=ldate_of_month)
    if request.method == 'POST':
        # Lấy ngày từ trên form về
        ngaydau = request.form.get('ngaydau')
        ngaycuoi = request.form.get('ngaycuoi')
        try:
            danhsachbc = utils.get_baocao(current_page,
                                          5,
                                          firstDate=ngaydau,
                                          lastDate=ngaycuoi)
            return render_template('bacsi_baocao.html',
                                   danhsach=danhsachbc,
                                   fdate=fdate_of_month,
                                   ldate=ldate_of_month)
        except:
            print("Không lấy được ngày")
    return render_template('bacsi_baocao.html',
                           danhsach=danhsachbc,
                           fdate=fdate_of_month,
                           ldate=ldate_of_month)


#--------------------ADMIN---------------------
@login.user_loader
def user_load(user_id):
    return TaiKhoan.query.get(user_id)


#-------------Tạo APP với những route trên----------
def create_app():
    app.register_blueprint(yta, url_prefix='/yta')
    app.register_blueprint(bacsi, url_prefix='/bacsi')
    app.register_blueprint(user, url_prefix='/')
    return app
