import asyncio
import json
import threading
import websockets

from turtle import Screen, Turtle


async def websocket_client():
    global websocket

    async with websockets.connect(server_uri) as ws:
        websocket = ws

        while True:
            try:
                message = await websocket.recv()
                positions = json.loads(message)
                action_queue.append(positions)
            except json.JSONDecodeError:
                pass


def start_websocket_client():
    asyncio.set_event_loop(loop)
    loop.run_until_complete(websocket_client())


def redraw():
    while action_queue:
        positions = action_queue.pop()

        for client_id, pos in positions.items():
            t.color(pos["color"])
            t.goto(pos["x"], pos["y"])
            t.stamp()


def send_position(x, y):
    if websocket and websocket.open:
        position = json.dumps({"x": x, "y": y})
        asyncio.run_coroutine_threadsafe(websocket.send(position), loop)


def on_motion(event):
    x = event.x - screen.window_width() / 2
    y = -event.y + screen.window_height() / 2
    send_position(x, y)


def tick():
    redraw()
    screen.update()
    screen.ontimer(tick, 1000 // 30)


server_uri = "wss://turtle-draw.onrender.com"
t = Turtle()
t.shape("circle")
t.penup()
screen = Screen()
screen.tracer(0)
action_queue = []
websocket = None
loop = asyncio.new_event_loop()
websocket_thread = threading.Thread(target=start_websocket_client, daemon=True)
websocket_thread.start()
screen.listen()
canvas = screen.getcanvas()
canvas.bind("<Motion>", on_motion)
tick()
screen.exitonclick()

