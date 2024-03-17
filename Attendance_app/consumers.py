from datetime import timedelta, datetime

from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio

from django.shortcuts import get_object_or_404
from asgiref.sync import sync_to_async
from Attendance_app.models import AttendanceUser
from pricing.models import Profile

import json

class MyConsumer(AsyncWebsocketConsumer):
    async def connect(self):

        self.group_name = 'group_name'
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        await self.update_duration_view()

    async def update_duration_view(self,):
        try:

            user__id = self.user_id
            attend = await sync_to_async(AttendanceUser.objects.get)(user_id=user__id, in_progress=True)
            attend.end = datetime.now().time()
            # Calculate the duration of working time
            job_time = datetime.combine(datetime.min, attend.end) - datetime.combine(datetime.min, attend.start)
            profile = await sync_to_async(Profile.objects.get)(user_id=user__id)
            # Calculate the number of hours elapsed since the record was created
            if attend.created_date < datetime.now().date():
                date_hours = datetime.now().date() - attend.created_date
                if job_time.days == date_hours.days:
                    await sync_to_async(attend.save)()
                    job_time = timedelta(seconds=job_time.total_seconds())

                    inc = round(profile.profile_position.position_income * (attend.job_time.total_seconds() / 3600), 4)
                    attend.job_time += job_time  # Convert to timedelta object

                    duration_formatted = str(attend.job_time).split(".")[0]  # Extract the hours:minutes:seconds part
                    duration_formatted = duration_formatted.replace("day", "روز")  # Replace "day" with "روز"
                    await self.send(text_data=f'{{"duration": "{duration_formatted}", "inc": {inc}}}')
                else:
                    # Add 24 hours for each day that has passed
                    job_time += timedelta(days=date_hours.days)
                    attend.save()
                    job_time = timedelta(seconds=job_time.total_seconds())
                    attend.job_time += job_time  # Convert to timedelta object
                    inc = round(profile.profile_position.position_income * (attend.job_time.total_seconds() / 3600), 4)
                    duration_formatted = str(attend.job_time).split(".")[0]  # Extract the hours:minutes:seconds part
                    duration_formatted = duration_formatted.replace("day", "روز")  # Replace "day" with "روز"
                    await self.send(text_data=f'{{"duration": "{duration_formatted}", "inc": {inc}}}')
            else:
                await sync_to_async(attend.save)()
                job_time = timedelta(seconds=job_time.total_seconds())
                attend.job_time += job_time  # Convert to timedelta object

                profile = await sync_to_async(Profile.objects.get)(user_id=user__id)
                position_income = await sync_to_async(lambda: profile.profile_position.position_income)()
                job_time_seconds = await sync_to_async(lambda: attend.job_time.total_seconds())()
                inc = await sync_to_async(round)((position_income * (job_time_seconds / 3600)), 4)

                duration_formatted = str(attend.job_time).split(".")[0]  # Extract the hours:minutes:seconds part
                await self.send(text_data=f'{{"duration": "{duration_formatted}", "inc": {inc}}}')
        except AttendanceUser.DoesNotExist:
            await self.send(text_data='{"duration": "0:00:00"}')
