# 服务器端 (server.py)
import asyncio
import websockets

async def chat(websocket, path):
    try:
        async for message in websocket:
            print(f"接收到消息: {message}")
            # 将消息广播给所有连接的客户端
            await broadcast(message)
    finally:
        await unregister(websocket)

clients = set()

async def register(websocket):
    clients.add(websocket)

async def unregister(websocket):
    clients.remove(websocket)

async def broadcast(message):
    for client in clients:
        await client.send(message)

async def main():
    server = await websockets.serve(chat, "0.0.0.0", 8765)
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())

# 客户端 (client.py)
import asyncio
import websockets

async def receive_messages(websocket):
    while True:
        message = await websocket.recv()
        print(f"收到消息: {message}")

async def send_messages(websocket):
    while True:
        message = input("输入消息: ")
        await websocket.send(message)

async def main():
    uri = "ws://服务器IP地址:8765"
    async with websockets.connect(uri) as websocket:
        receive_task = asyncio.create_task(receive_messages(websocket))
        send_task = asyncio.create_task(send_messages(websocket))
        await asyncio.gather(receive_task, send_task)

if __name__ == "__main__":
    asyncio.run(main())