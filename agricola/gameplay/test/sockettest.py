import asyncio
import websockets
import json

async def connect_websocket():
    uri = "ws://127.0.0.1:8000/ws/agricola1/player_1/"
    async with websockets.connect(uri) as websocket:
        # Create a JSON message with the desired request type
        message = json.dumps({
            'type': 'get_account_data'
        })
        # print(f'message: {message}')

        # Send the JSON message through the websocket
        print('websocket.send(message)')
        await websocket.send(message)

        # Wait for the response
        response = await websocket.recv()
        print(f"Received response: {response}")

if __name__ == '__main__':
    asyncio.run(connect_websocket())
