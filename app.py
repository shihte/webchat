# 服务器端代码 (server.py)

import asyncio
import websockets

# 存储所有连接的客户端
clients = set()

async def handle_client(websocket, path):
    # 注册新客户端
    clients.add(websocket)
    try:
        async for message in websocket:
            # 打印接收到的消息
            print(f"收到消息: {message}")
            # 广播消息给所有客户端
            await broadcast(message)
    finally:
        # 客户端断开连接时移除
        clients.remove(websocket)

async def broadcast(message):
    # 向所有连接的客户端发送消息
    for client in clients:
        try:
            await client.send(message)
        except websockets.exceptions.ConnectionClosed:
            pass  # 忽略已关闭的连接

async def main():
    # 启动WebSocket服务器
    server = await websockets.serve(handle_client, "0.0.0.0", 8765)
    print("服务器已启动，等待客户端连接...")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())

# 客户端代码 (client.py)

import asyncio
import websockets

async def receive_messages(websocket):
    # 持续接收服务器发送的消息
    while True:
        try:
            message = await websocket.recv()
            print(f"收到消息: {message}")
        except websockets.exceptions.ConnectionClosed:
            print("连接已关闭")
            break

async def send_messages(websocket):
    # 持续从控制台读取输入并发送消息
    while True:
        message = input("输入消息 (输入 'quit' 退出): ")
        if message.lower() == 'quit':
            break
        await websocket.send(message)

async def main():
    # 服务器的WebSocket URL
    uri = "ws://localhost:8765"  # 如果服务器不在本地，请替换为实际IP地址
    async with websockets.connect(uri) as websocket:
        print("已连接到服务器")
        # 创建接收和发送消息的任务
        receive_task = asyncio.create_task(receive_messages(websocket))
        send_task = asyncio.create_task(send_messages(websocket))
        # 等待任意一个任务完成
        await asyncio.gather(receive_task, send_task)

if __name__ == "__main__":
    asyncio.run(main())