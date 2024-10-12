import socket

def main():
    # 創建一個 IPv4 TCP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # 綁定到所有可用的網絡接口和端口 1234
        s.bind(("0.0.0.0", 1234))
        
        # 開始監聽連接請求
        s.listen()
        print("Server is listening on 0.0.0.0:1234")
        
        while True:
            # 接受客戶端連接
            c, addr = s.accept()
            with c:
                print(f"Connected by {addr}")
                
                while True:
                    # 從客戶端接收數據
                    data = c.recv(1024)
                    if not data:
                        # 如果沒有數據，表示客戶端已斷開連接
                        print(f"Connection from {addr} closed.")
                        break
                    
                    # 將接收到的數據打印出來
                    print(f"Received from {addr}: {data.decode('utf-8')}")
                    
                    # 將數據發送回客戶端
                    c.sendall(data)
                    print(f"Echoed back to {addr}")

if __name__ == "__main__":
    main()