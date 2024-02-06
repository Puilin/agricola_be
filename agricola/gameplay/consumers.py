import json
import requests
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from .models import *
from .serializer import *
from random import shuffle, choice
from asgiref.sync import sync_to_async
from gameplay.views import *
from django.core.handlers.base import BaseHandler
from django.test import RequestFactory
from django.test.client import Client

class Consumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name'] # agricola1
        self.player_id = self.scope['url_route']['kwargs']['player_id'] # 1 혹은 2
        self.room_group_name = 'group_%s' % self.room_name # group_agricola1

        # 방이 존재하지 않으면 방을 생성합니다.
        if not await self.room_exists():
            await self.create_room()

        # 방 그룹에 연결합니다.
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'socket_message',
                'message': f'connected to room {self.room_name} with {self.player_id}'
            }
        )

    async def disconnect(self, close_code):
        # 방 그룹에서 연결을 제거합니다.
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    @database_sync_to_async
    def room_exists(self):
        return Room.objects.filter(name=self.room_name).exists()

    @database_sync_to_async
    def create_room(self):
        Room.objects.create(name=self.room_name)


    async def socket_message(self, event):
        await self.send_json(event['message'])

    async def game_message(self, event):
        await self.send_json(event['message'])
    
    async def api_response(self, event):
        await self.send(event['message']['data'])

    async def get_account_data(self):
        accounts = await sync_to_async(Account.objects.all)()
        serializer = AccountSerializer(accounts, many=True)
        return serializer.data