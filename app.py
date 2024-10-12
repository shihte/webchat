import asyncio
import websockets
import socket
import json

# 存儲所有連接的客戶端
clients = set()

# 聊天記錄
chat_history = []

async def handle_client(websocket, path):
    clients.add(websocket)
    try:
        # 發送聊天歷史
        await websocket.send(json.dumps({"type": "history", "messages": chat_history}))
        
        async for message in websocket:
            data = json.loads(message)
            if data["type"] == "chat":
                chat_message = f"{data['name']}: {data['message']}"
                chat_history.append(chat_message)
                if len(chat_history) > 100:  # 限制歷史記錄數量
                    chat_history.pop(0)
                print(chat_message)
                await broadcast(json.dumps({"type": "chat", "message": chat_message}))
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
    print(f"服務器正在運行於 {host}:{port}")
    await server.wait_closed()

async def client_receive(websocket):
    try:
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            if data["type"] == "history":
                print("聊天歷史:")
                for msg in data["messages"]:
                    print(msg)
            elif data["type"] == "chat":
                print(data["message"])
    except websockets.exceptions.ConnectionClosed:
        print("連接已關閉")

async def client_send(websocket, name):
    try:
        while True:
            message = await asyncio.get_event_loop().run_in_executor(None, input, "")
            if message.lower() == 'quit':
                break
            await websocket.send(json.dumps({"type": "chat", "name": name, "message": message}))
    except asyncio.CancelledError:
        pass

async def start_client(uri, name):
    async with websockets.connect(uri) as websocket:
        print(f"已連接到 {uri}")
        receive_task = asyncio.create_task(client_receive(websocket))
        send_task = asyncio.create_task(client_send(websocket, name))
        await asyncio.gather(receive_task, send_task)

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"

async def main():
    host = get_local_ip()
    port = 8765
    name = input("請輸入您的名字: ")
    
    try:
        # 首先嘗試作為客戶端連接
        await start_client(f"ws://{host}:{port}", name)
    except ConnectionRefusedError:
        print("無法連接到現有服務器，正在啟動新的服務器...")
        await start_server(host, port)

if __name__ == "__main__":
    asyncio.run(main())