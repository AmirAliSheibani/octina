import json
import asyncio
from datetime import datetime, timedelta
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

User = get_user_model()


class AttendanceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """ اتصال وب‌سوکت """
        self.user = self.scope["user"]
        if self.user.is_authenticated:
            await self.accept()
            asyncio.create_task(self.send_duration_periodically())  # اجرای حلقه ارسال خودکار
        else:
            await self.close()

    async def disconnect(self, close_code):
        """ قطع اتصال """
        print("WebSocket Disconnected")

    async def send_duration_periodically(self):
        """ هر ۵ ثانیه مقدار جدید duration رو می‌فرسته """
        while True:
            duration = await self.get_duration()
            if duration:
                await self.send(text_data=json.dumps({
                    "duration": str(timedelta(seconds=int(duration.total_seconds())))
                }))
            await asyncio.sleep(1)  # هر ۵ ثانیه ارسال کنه

    @database_sync_to_async
    def get_last_attendance(self):
        """ دریافت آخرین حضور کاربر """
        return self.user.user_attendance.order_by("-created_date").first()

    async def get_duration(self):
        """ محاسبه مدت زمان کارکرد """
        attendance = await self.get_last_attendance()
        if not attendance:
            return None

        now = datetime.now().time()
        return attendance.job_time + (
                datetime.combine(datetime.min, now) - datetime.combine(datetime.min, attendance.start))
