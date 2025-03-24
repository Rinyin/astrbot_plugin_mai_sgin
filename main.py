from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from datetime import datetime, timedelta
from .user_data import UserData

@register("mai_sgin", "Rinyin", "maimai出勤签到插件", "1.0.0")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.user_checkin_data = {}  # 用于存储用户签到信息的字典
        self.user_data = {}  # 用于存储用户出退勤信息的字典
        self.user_backup_data = {}  # 用于备份用户数据的字典
    
    @filter.command_group("mai")
    def mai(self):
        pass

    @mai.command("in")
    async def mai_in(self, event: AstrMessageEvent, time_str: str = None):
        user_id = event.get_sender_id()  # 获取用户ID
        if time_str:
            try:
                time_str = time_str.replace('：', ':')  # 将全角冒号替换为半角冒号
                time = datetime.strptime(time_str, "%H:%M").time()  # 解析时间参数
                date = datetime.now().date()  # 使用当前日期
            except ValueError:
                yield event.plain_result("时间格式错误，请使用 HH:MM 格式")
        else:
            current_time = datetime.now()  # 获取当前时间
            date = current_time.date()  # 获取日期
            time = current_time.time()  # 获取时间
        self.user_checkin_data[user_id] = {"date": date, "time": time}  # 存储用户的签到信息
        if user_id not in self.user_data:
            self.user_data[user_id] = UserData()  # 初始化用户数据
        logger.info(f"用户 {user_id} 签到日期: {date}, 签到时间: {time}")  # 记录日志
        yield event.plain_result("舞萌，启动！")
    
    @mai.command("out")
    async def mai_out(self, event: AstrMessageEvent, time_str: str = None, new_rt: int = None):
        user_id = event.get_sender_id()
        if user_id in self.user_checkin_data:
            if time_str:
                try:
                    time_str = time_str.replace('：', ':')  # 将全角冒号替换为半角冒号
                    out_time = datetime.strptime(time_str, "%H:%M").time()  # 解析时间参数
                    out_date = datetime.now().date()  # 使用当前日期
                except ValueError:
                    yield event.plain_result("时间格式错误，请使用 HH:MM 格式")
            else:
                checkin_data = self.user_checkin_data[user_id]
                out_date = checkin_data["date"]
                out_time = checkin_data["time"]
            
            checkin_data = self.user_checkin_data[user_id]
            in_datetime = datetime.combine(checkin_data["date"], checkin_data["time"])
            out_datetime = datetime.combine(out_date, out_time)
            duration = out_datetime - in_datetime
            
            if duration > timedelta(hours=12):
                yield event.plain_result("勤12小时？超人来的？")
            
            if new_rt is not None:
                if 0 <= new_rt <= 1000:
                    self.user_data[user_id].add_checkin(duration, out_date, new_rt)  # 更新用户数据
                    logger.info(f"用户 {user_id} 签到日期: {checkin_data['date']}, 签到时间: {checkin_data['time']}")
                    logger.info(f"用户 {user_id} 退勤日期: {out_date}, 退勤时间: {out_time}")
                    yield event.plain_result(f"退勤成功，你今天勤了 {duration} 小时哦！今天涨了{new_rt}分，你现在的rating是{self.user_data[user_id].rating}")
                else:
                    yield event.plain_result("开了？")
            else:
                self.user_data[user_id].add_checkin(duration, out_date)  # 更新用户数据
                logger.info(f"用户 {user_id} 签到日期: {checkin_data['date']}, 签到时间: {checkin_data['time']}")
                logger.info(f"用户 {user_id} 退勤日期: {out_date}, 退勤时间: {out_time}")
                yield event.plain_result(f"退勤成功，你今天勤了 {duration} 小时哦！")
        else:
            yield event.plain_result("没出勤就退勤，你是在玩ADX？")
    
    @mai.command("rating")
    async def mai_rating(self, event: AstrMessageEvent, rating: int):
        user_id = event.get_sender_id()
        if 0 <= rating <= 16547:
            if user_id not in self.user_data:
                self.user_data[user_id] = UserData()  # 初始化用户数据
            self.user_data[user_id].rating = rating  # 更新用户的 rating
            logger.info(f"用户 {user_id} 的 rating 更新为 {rating}")
            yield event.plain_result(f"你的 rating 已更新为 {rating}")
        else:
            yield event.plain_result("rating 应在 0 到 16547 之间")
        
    @mai.command("day")
    async def mai_day(self, event: AstrMessageEvent):
        user_id = event.get_sender_id()
        if user_id in self.user_data:
            yield event.plain_result(f"你的总出勤天数是 {self.user_data[user_id].total_checkin_days}")
        else:
            yield event.plain_result("懒比")
        
    @mai.command("time")
    async def mai_time(self, event: AstrMessageEvent):
        user_id = event.get_sender_id()
        if user_id in self.user_data:
            yield event.plain_result(f"你的总出勤时间是 {self.user_data[user_id].total_checkin_time}")
        else:
            yield event.plain_result("懒比")
        
    @mai.command("rt")
    async def mai_rt_view(self, event: AstrMessageEvent):
        user_id = event.get_sender_id()
        if user_id in self.user_data:
            yield event.plain_result(f"你的 rating 是 {self.user_data[user_id].rating}")
        else:
            yield event.plain_result("请先使用 /rating rt值 更新rating")

    @mai.command("reset")
    async def mai_reset(self, event: AstrMessageEvent):
        user_id = event.get_sender_id()
        if user_id in self.user_data:
            self.user_backup_data[user_id] = self.user_data[user_id]  # 备份用户数据
            self.user_data[user_id] = UserData()  # 重置用户数据
            yield event.plain_result("你的数据已重置")
        else:
            yield event.plain_result("没有找到你的数据")

    @mai.command("unreset")
    async def mai_unreset(self, event: AstrMessageEvent):
        user_id = event.get_sender_id()
        if user_id in self.user_backup_data:
            self.user_data[user_id] = self.user_backup_data.pop(user_id)  # 恢复备份数据
            yield event.plain_result("你的数据已恢复")
        else:
            yield event.plain_result("没有找到你的备份数据")

    @mai.command("help")
    async def mai_help(self, event: AstrMessageEvent):
        yield event.plain_result("/mai help（获取帮助）\n"
                                  "/mai in [HH:MM](出勤签到)\n"
                                  "/mai out [HH:MM] [add_rt]（退勤签到）\n"
                                  "/mai rating <rt值>（更新rating）\n"
                                  "/mai day（获取出勤天数）\n"
                                  "/mai time（获取出勤时间）\n"
                                  "/mai rt（获取rating）\n"
                                  "/mai reset（重置数据）\n"
                                  "/mai unreset（恢复数据）")
