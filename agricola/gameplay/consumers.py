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
        client = Client()
        client.get('/account/initial/')
        await self.accept()
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'game_message',
                'message': 'initial complete.'
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

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        request_type = text_data_json.get('type')

        
        try:
            if request_type == 'get_account_data':
                account_data = await self.get_account_data()
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'game_message',
                        'message': account_data
                    }
                )
            if request_type == 'build_fence':
                await self.build_fence(text_data_json.get('fence_array'))

            if request_type == 'choose_first_player':
                fst_player = await self.choose_first_player()
                await self.send_json(fst_player)

            if request_type == 'get_random_subfacilitycards':
                random_cards = await self.get_random_subfacilitycards()
                await self.send_json(random_cards)

            if request_type == 'get_random_jobcards':
                random_cards = await self.get_random_jobcards()
                await self.send_json(random_cards)

            if request_type == 'get_turn':
                await self.get_turn()

            if request_type == 'take_action':
                await self.take_action(text_data_json)
            
            if request_type == 'get_player_resource':
                await self.get_player_resource(text_data_json)

            if request_type == 'get_all_position':
                await self.get_all_position(text_data_json)
            
            if request_type == 'update_player_resource':
                await self.update_player_resource(text_data_json)
            
            if request_type == 'patch_boardposition':
                await self.patch_boardposition(text_data_json)
            
            if request_type == 'post_penposition':
                await self.post_penposition(text_data_json)
            
            if request_type == 'activate_card':
                await self.activate_card(text_data_json)
            
            if request_type == 'raise_animal':
                await self.raise_animal(text_data_json)
            
            if request_type == 'construct_land':
                await self.construct_land(text_data_json)
            
            if request_type == 'construct_room':
                await self.construct_room(text_data_json)
            
            if request_type == 'construct_cowshed':
                await self.construct_cowshed(text_data_json)

            if request_type == 'login':
                await self.login(text_data_json)

            if request_type == 'get_available_slots':
                await self.get_available_slots(text_data_json)
        except:
            await self.channel_layer.group_send(self.room_group_name, {'type':'game_message', 'message':'Invalid API formula'})

    async def game_message(self, event):
        await self.send_json(event['message'])
    
    async def api_response(self, event):
        await self.send(event['message']['data'])

    async def get_account_data(self):
        accounts = await sync_to_async(Account.objects.all)()
        serializer = AccountSerializer(accounts, many=True)
        return serializer.data

    async def choose_first_player(self):
        players = Player.objects.all()

        if players.exists():
            first_player = choice(players)
            players.update(fst_player=False)
            first_player.fst_player = True
            first_player.save()

            serializer = PlayerSerializer(first_player)
            return serializer.data
        else:
            return "No players found."

    async def get_random_subfacilitycards(self):
        subfacilitycards = list(SubFacilityCard.objects.all())
        shuffle(subfacilitycards)  # 리스트를 랜덤하게 섞습니다.

        chunked_subcards = [subfacilitycards[i:i + 7] for i in range(0, 14, 7)]  # 7개씩 두 묶음으로 나눕니다.
        serialized_data = []

        for chunk in chunked_subcards:
            serializer = SubFacilityCardSerializer(chunk, many=True)
            serialized_data.append(serializer.data)

        return serialized_data

    async def get_random_jobcards(self):
        jobcards = list(JobCard.objects.all())
        shuffle(jobcards)  # 리스트를 랜덤하게 섞습니다.

        chunked_subcards = [jobcards[i:i + 7] for i in range(0, 14, 7)]  # 7개씩 두 묶음으로 나눕니다.
        serialized_data = []

        for chunk in chunked_subcards:
            serializer = JobCardSerializer(chunk, many=True)
            serialized_data.append(serializer.data)

        return serialized_data

    async def get_turn(self):
        game_status = self.get_queryset().first()  # Assuming there is only one GameStatus instance
        turn_counter = game_status.turn
        await self.send_json({'turn': turn_counter})

    # 이렇게 view에서 만든 api 재활용 가능
    async def take_action(self, request):
        turn = request.get('turn')
        player_id = request.get('player_id')
        action_id = request.get('action_id')
        card_id = request.get('card_id')

        factory = RequestFactory()
        http_request = factory.post('/familyposition/take_action/', {'turn': turn, 'player_id': player_id, 'action_id': action_id, 'card_id': card_id})

        client = Client()
        response = client.post('/familyposition/take_action/', {'turn': turn, 'player_id': player_id, 'action_id': action_id, 'card_id': card_id})

        # Retrieve the response content
        content = response.content

        # Construct a JSON response
        json_response = {
            'status': response.status_code,
            'data': content.decode(),
        }

        result = {
            'type': 'api_response',
            'message': json_response
        }

        await self.channel_layer.group_send(message=result, group=self.room_group_name)


    async def update_player_resource(self, request):
        player_id = request.get('player_id')
        resource_id = request.get('resource_id')
        num = request.get('num')

        factory = RequestFactory()
        http_request = factory.put('/playerresource/update_player_resource/', {'player_id': player_id, 'resource_id': resource_id, 'num': num})

        client = Client()
        response = client.put('/playerresource/update_player_resource/', {'player_id': player_id, 'resource_id': resource_id, 'num': num}, content_type="application/json")

        # Retrieve the response content
        content = response.content

        # Construct a JSON response
        json_response = {
            'status': response.status_code,
            'data': content.decode(),
        }

        result = {
            'type': 'api_response',
            'message': json_response
        }

        await self.channel_layer.group_send(message=result, group=self.room_group_name)
    
    # 이렇게 view에서 만든 api 재활용 가능
    async def get_player_resource(self, request):
        player_id = int(request.get('player_id'))
        resource_id = int(request.get('resource_id'))

        factory = RequestFactory()
        http_request = factory.get('/playerresource/get_player_resource/', {'player_id': player_id, 'resource_id': resource_id})

        client = Client()
        response = client.get('/playerresource/get_player_resource/', {'player_id': player_id, 'resource_id': resource_id})

        result = {
            'type': 'api_response',
            'message': response.data
        }

        await self.channel_layer.group_send(message=result, group=self.room_group_name)

    async def build_fence(self, fence_array): # { 'fence_array': [[3, 4], [5, 6]] }
        fence_array = json.loads(fence_array)
        client = Client()
        response = client.post('/fenceposition/build_fence/', {'player_id': self.player_id, 'fence_array': str(fence_array)})
        content = response.content
        json_response = {
            'status': response.status_code,
            'data': content.decode(),
        }

        result = {
            'type': 'api_response',
            'message': json_response
        }
        await self.channel_layer.group_send(
            message= result,
            group=self.room_group_name
        )

    async def get_all_position(self, request):
        player_id = request.get('player_id')

        factory = RequestFactory()
        http_request = factory.post('/boardposition/get_all_position/', {'player_id': player_id})

        client = Client()
        response = client.post('/boardposition/get_all_position/', {'player_id': player_id})

        # Retrieve the response content
        content = response.content

        # Construct a JSON response
        json_response = {
            'status': response.status_code,
            'data': content.decode(),
        }

        result = {
            'type': 'api_response',
            'message': json_response
        }

        await self.channel_layer.group_send(message=result, group=self.room_group_name)
    
    # 안됨
    async def patch_boardposition(self, request):
        
        id = request.get('id')
        position = request.get('position')
        position_type = request.get('position_type')
        is_fam = request.get('is_fam')
        vege_type = request.get('vege_type')
        vege_num = request.get('vege_num')
        animal_num = request.get('animal_num')
        board_id = request.get('board_id')
        
        req_body = {
            'id': int(id),
            'position': position,
            'position_type': position_type,
            'is_fam': is_fam,
            'vege_type': vege_type,
            'vege_num': vege_num,
            'animal_num': animal_num,
            'board_id': board_id
        }

        factory = RequestFactory()
        http_request = factory.patch('/boardposition/{}/'.format(id), req_body)

        client = Client()
        response = client.patch('/boardposition/{}/'.format(id), req_body, content_type="application/json")

        # Retrieve the response content
        content = response.content

        # Construct a JSON response
        json_response = {
            'status': response.status_code,
            'data': content.decode(),
        }

        result = {
            'type': 'api_response',
            'message': json_response
        }

        await self.channel_layer.group_send(message=result, group=self.room_group_name)

    async def post_penposition(self, request):
        animal_type = request.get('animal_type')
        max_num = request.get('max_num')
        current_num = request.get('current_num')
        position_list = request.get('position_list')
        board_id = request.get('board_id')

        req_body = {
            "animal_type": animal_type,
            "max_num": max_num,
            "current_num": current_num,
            "position_list": position_list,
            "board_id": board_id
        }

        factory = RequestFactory()
        http_request = factory.post('/penposition/', req_body)

        client = Client()
        response = client.post('/penposition/', req_body)

        # Retrieve the response content
        content = response.content

        # Construct a JSON response
        json_response = {
            'status': response.status_code,
            'data': content.decode(),
        }

        result = {
            'type': 'api_response',
            'message': json_response
        }

        await self.channel_layer.group_send(message=result, group=self.room_group_name)

    async def activate_card(self, request):
        activate = request.get('activate')
        player_id = request.get('player_id')
        card_id = request.get('card_id')

        req_body = {
            "activate": activate,
            "player_id": player_id,
            "card_id": card_id
        }

        factory = RequestFactory()
        http_request = factory.put('/playercard/activate_card/', req_body)

        client = Client()
        response = client.put('/playercard/activate_card/', req_body, content_type='application/json')

        # Retrieve the response content
        content = response.content

        # Construct a JSON response
        json_response = {
            'status': response.status_code,
            'data': content.decode(),
        }

        result = {
            'type': 'api_response',
            'message': json_response
        }

        await self.channel_layer.group_send(message=result, group=self.room_group_name)

    async def raise_animal(self, request):
        player_id = request.get('player_id')
        animal_type = request.get('animal_type')
        position = request.get('position')

        req_body = {
            "player_id": 1,
            "animal_type": 1,
            "position": 7
        }
        

        factory = RequestFactory()
        http_request = factory.put('/playerboardstatus/raise_animal/', req_body)

        client = Client()
        response = client.put('/playerboardstatus/raise_animal/', req_body, content_type='application/json')

        # Retrieve the response content
        content = response.content

        # Construct a JSON response
        json_response = {
            'status': response.status_code,
            'data': content.decode(),
        }

        result = {
            'type': 'api_response',
            'message': json_response
        }

        await self.channel_layer.group_send(message=result, group=self.room_group_name)

    async def construct_land(self, request):
        player_id = request.get('player_id')
        land_num = request.get('land_num')

        req_body = {
            "player_id": player_id,
            "land_num": land_num
        }

        factory = RequestFactory()
        http_request = factory.put('/boardposition/construct_land/', req_body)

        client = Client()
        response = client.put('/boardposition/construct_land/', req_body, content_type='application/json')

        # Retrieve the response content
        content = response.content

        # Construct a JSON response
        json_response = {
            'status': response.status_code,
            'data': content.decode(),
        }

        result = {
            'type': 'api_response',
            'message': json_response
        }

        await self.channel_layer.group_send(message=result, group=self.room_group_name)

    async def construct_room(self, request):
        player_id = request.get('player_id')
        position = request.get('position')

        req_body = {
            "player_id": player_id,
            "position": position
        }

        factory = RequestFactory()
        http_request = factory.put('/boardposition/construct_room/', req_body)

        client = Client()
        response = client.put('/boardposition/construct_room/', req_body, content_type='application/json')

        # Retrieve the response content
        content = response.content

        # Construct a JSON response
        json_response = {
            'status': response.status_code,
            'data': content.decode(),
        }

        result = {
            'type': 'api_response',
            'message': json_response
        }

        await self.channel_layer.group_send(message=result, group=self.room_group_name)

    async def construct_cowshed(self, request):
        player_id = request.get('player_id')
        position = request.get('position')

        req_body = {
            "player_id": player_id,
            "position": position
        }

        factory = RequestFactory()
        http_request = factory.put('/boardposition/construct_cowshed/', req_body)

        client = Client()
        response = client.put('/boardposition/construct_cowshed/', req_body, content_type='application/json')

        # Retrieve the response content
        content = response.content

        # Construct a JSON response
        json_response = {
            'status': response.status_code,
            'data': content.decode(),
        }

        result = {
            'type': 'api_response',
            'message': json_response
        }

        await self.channel_layer.group_send(message=result, group=self.room_group_name)

    async def login(self, request):
        user_id = request.get('user_id')
        user_pw = request.get('user_pw')
        
        req_body = {
            "user_id": user_id,
            "user_pw": user_pw
        }

        factory = RequestFactory()
        http_request = factory.post('/account/login/', req_body)

        client = Client()
        response = client.post('/account/login/', req_body, content_type='application/json')

        # Retrieve the response content
        content = response.content

        # Construct a JSON response
        json_response = {
            'status': response.status_code,
            'data': content.decode(),
        }

        result = {
            'type': 'api_response',
            'message': json_response
        }

        await self.channel_layer.group_send(message=result, group=self.room_group_name)
    
    async def get_available_slots(self, request):
        player_id = request.get('player_id')
        slot_type = request.get('slot_type')

        req_body = {
            "player_id" : player_id,
            "slot_type" : slot_type
        }

        factory = RequestFactory()
        http_request = factory.get('/boardposition/get_available_slots/', req_body)

        client = Client()
        response = client.get('/boardposition/get_available_slots/', req_body, content_type='application/json')

        # Retrieve the response content
        content = response.content

        # Construct a JSON response
        json_response = {
            'status': response.status_code,
            'data': content.decode(),
        }

        result = {
            'type': 'api_response',
            'message': json_response
        }

        await self.channel_layer.group_send(message=result, group=self.room_group_name)