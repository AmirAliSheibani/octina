import json
from datetime import datetime, timezone, timedelta
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

class AttendanceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_authenticated:
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        pass  # می‌توانید عملیات خاصی در زمان قطع اتصال انجام دهید

    async def receive(self, text_data):
        """ دریافت پیام از WebSocket و بروزرسانی اطلاعات """
        await self.update_duration_view()

    @database_sync_to_async
    def get_profile(self):
        """ دریافت پروفایل کاربر """
        return self.user.possit

    @database_sync_to_async
    def get_profile_position(self, profile):
        """ دریافت موقعیت پروفایل (Profile Position) """
        return profile.profile_position

    @database_sync_to_async
    def get_last_attendance(self):
        """ دریافت آخرین حضور کاربر """
        return self.user.user_attendance.last()

    @database_sync_to_async
    def get_last_income(self):
        """ دریافت آخرین درآمد """
        return self.user.user_incomes.last().user_income



    async def update_duration_view(self):
        """ محاسبه مدت زمان و درآمد کاربر و ارسال اطلاعات به WebSocket """
        profile = await self.get_profile()
        profile_position = await self.get_profile_position(profile)


        attendance = await self.get_last_attendance()
        print(attendance)
        print(attendance.overtime_check)
        if attendance:
            now = datetime.now().time()
            duration = attendance.job_time
            duration += datetime.combine(datetime.min, now) - datetime.combine(datetime.min, attendance.start)

        else:
            duration = 0

        if profile_position.monthly:
            income = await self.get_last_income()

        else:
            income = profile_position.position_income * (duration / 3600)

        print(income)
        print(duration)
        print(attendance.created_date)
        data = {
            "income": str(income),
            "duration": str(timedelta(seconds=int(duration.total_seconds())))
        }

        await self.send(text_data=json.dumps(data))
