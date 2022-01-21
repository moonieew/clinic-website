from datetime import datetime, timedelta
import calendar
#Xử lí một số vấn đề về thời gian
# Lấy thời gian ngày hôm nay [ngày và giờ hiện tại]
today_str = datetime.today()
# Chuyển thời gian lấy được qua String
date_str = today_str.strftime("%Y-%m-%d")
# Chuyển thời gian từ String qua DateTime [ngày hiện tại, giờ 00:00:00]
today = today_str.strptime(date_str, "%Y-%m-%d")
yesterday = today - timedelta(days=1)
tomorrow = today + timedelta(days=1)
yesterday = str(yesterday)
tomorrow = str(tomorrow)
# print("Biến today có giá trị là " + str(today) + " Kiểu dữ liệu là " +
#       str(type(today)))
# print("Biến yes có giá trị là " + str(yesterday) + " Kiểu dữ liệu là " +
#       str(type(yesterday)))
# print("Biến tom có giá trị là " + str(tomorrow) + " Kiểu dữ liệu là " +
#       str(type(tomorrow)))

# Lấy danh sách theo ngày phải lấy từ 0h ngày hôm nay đến 0h hôm nay
today = datetime.today().date()

d = today.replace(day=calendar.monthrange(today.year, today.month)[1])
print(d)
h = calendar.monthrange(today.year, today.month)
print(h)