from datetime import timedelta
import datetime

class UserData:
    def __init__(self):
        self.checkin_count = 0  # 出勤次数
        self.total_checkin_time = timedelta()  # 总出勤时间
        self.total_checkin_days = 0  # 总出勤天数
        self.rating = 0  # rating
        self.daily_rating = {}  # 每天增长 rating
        self.checkin_rating = {}  # 每次出勤增长 rating

    def add_checkin(self, duration: timedelta, date: datetime.date, new_rt: int = 0):
        self.checkin_count += 1
        self.total_checkin_time += duration
        if date not in self.daily_rating:
            self.total_checkin_days += 1
            self.daily_rating[date] = 0
        self.daily_rating[date] += new_rt  # 更新当天的总 rating 增加
        self.checkin_rating[self.checkin_count] = new_rt
        self.rating = min(self.rating + new_rt, 16547)  # 更新总 rating

