PHẦN CLONE

1. Clone code về [git clone {linkgithub} -b <tên branch>] theo branch
   ex : git clone <link> -b master
2. Tạo thư môi trường ảo [virtualenv venv]
3. Chạy trong môi trường ảo [venv\Scripts\activate]
4. Cài đặt thư viện [pip install -r requirements.txt]
5. Vào [website/__init__.py] sửa root:password lại
6. Vào models.py kéo xuống cuối file bật hàm main lên chạy để tạo database, sau khi chạy xong thì comment code lại [Ctrl+/]
7. Tạo thư mục static trong website xong copy assets vào trong đó [website/static/assets]
8. Mở file run.py chạy web

PHẦN PUSH lên lại

1. Đẩy mới hết các code vừa xong vào [git add .]
2. Kiểm tra bằng lệnh [git status]
3. Nếu đã add vào hết rồi thì commit lại [git commit -m "Lời nhắn"]
4. Kiểm tra commit bằng lệnh [git log]
5. Nếu chưa có remote thì phải tạo bằng lệnh [git remote add origin <link lúc clone>]
6. Push code [git push origin]
