import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Card
from .serializer import CardSerializer

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        request_type = text_data_json.get('type')

        if request_type == 'get_card_data':
            card_data = await self.get_card_data()
            await self.send_json(card_data)

    async def get_card_data(self):
        cards = Card.objects.all()
        serializer = CardSerializer(cards, many=True)
        return {'type': 'card_data', 'data': serializer.data}
