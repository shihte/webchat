import asyncio
import websockets
import socket

# 存储所有连接的客户端
clients = set()

async def handle_client(websocket, path):
    clients.add(websocket)
    try:
        async for message in websocket:
            print(f"收到消息: {message}")
            await broadcast(message)
    finally:
        clients.remove(websocket)

async def broadcast(message):
    for client in clients:
        try:
            await client.send(message)
        except websockets.exceptions.ConnectionClosed:
            pass

async def start_server(host, port):
    server = await websockets.serve(handle_client, host, port)
    print(f"服务器正在运行于 {host}:{port}")
    await server.wait_closed()

async def client_receive(websocket):
    try:
        while True:
            message = await websocket.recv()
            print(f"收到: {message}")
    except websockets.exceptions.ConnectionClosed:
        print("连接已关闭")

async def client_send(websocket):
    try:
        while True:
            message = await asyncio.get_event_loop().run_in_executor(None, input, "输入消息: ")
            await websocket.send(message)
            if message.lower() == 'quit':
                break
    except asyncio.CancelledError:
        pass

async def start_client(uri):
    async with websockets.connect(uri) as websocket:
        print(f"已连接到 {uri}")
        receive_task = asyncio.create_task(client_receive(websocket))
        send_task = asyncio.create_task(client_send(websocket))
        await asyncio.gather(receive_task, send_task)

def get_local_ip():
    try:
        # 创建一个临时套接字连接到一个公共 DNS 服务器
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"

if __name__ == "__main__":
    print("WebSocket 聊天程序")
    print("1. 运行服务器")
    print("2. 运行客户端")
    choice = input("请选择模式 (1/2): ")

    if choice == "1":
        host = get_local_ip()
        port = 8765
        print(f"服务器将在 {host}:{port} 上运行")
        print(f"客户端可以使用以下地址连接：ws://{host}:{port}")
        asyncio.run(start_server(host, port))
    elif choice == "2":
        host = input("输入服务器 IP 地址 (默认为 localhost): ") or "localhost"
        port = input("输入服务器端口 (默认为 8765): ") or 8765
        uri = f"ws://{host}:{port}"
        asyncio.run(start_client(uri))
    else:
        print("无效的选择")