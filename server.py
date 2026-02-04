import asyncio
import json
import os
import websockets

from random import random

connected_clients = {}
positions = {}


async def websocket_handler(websocket, path):
    client_id = id(websocket)
    connected_clients[websocket] = client_id
    positions[client_id] = {"x": 0, "y": 0, "color": [random(), random(), random()]}
    print(f"Client {client_id} connected")

    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                if "x" in data and "y" in data:
                    positions[client_id]["x"] = data["x"]
                    positions[client_id]["y"] = data["y"]
            except json.JSONDecodeError:
                pass

    except websockets.ConnectionClosed:
        print(f"Client {client_id} disconnected")
    finally:
        del connected_clients[websocket]
        del positions[client_id]


async def game_loop():
    while True:
        if connected_clients:
            message = json.dumps(positions)
            disconnected_clients = set()

            for client in connected_clients:
                try:
                    await client.send(message)
                except websockets.ConnectionClosed:
                    disconnected_clients.add(client)

            for client in disconnected_clients:
                del positions[connected_clients[client]]
                del connected_clients[client]

        await asyncio.sleep(1 / 30)  # 30 FPS


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8765))
    start_server = websockets.serve(websocket_handler, "0.0.0.0", port)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_server)
    loop.create_task(game_loop())
    print(f"WebSocket server running on ws://0.0.0.0:{port}")
    loop.run_forever()

