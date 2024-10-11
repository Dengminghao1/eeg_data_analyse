import asyncio
import websockets
import json


async def send_json_message(websocket, code, sort, msg):
    """
    发送 JSON 格式的消息到 WebSocket 服务器
    """
    message = {
        "code": code,
        "sort": sort,
        "msg": msg
    }
    json_message = json.dumps(message)
    await websocket.send(json_message)
    print(f"Sent: {json_message}")


async def process_and_respond(websocket, message):
    """
    处理接收到的 JSON 消息，并发送处理结果到 WebSocket 服务器
    """
    try:
        data = json.loads(message)

        # 处理接收到的数据
        print(f"Processing received data: {data}")

        # 示例处理：修改数据并发送回服务器
        response = {
            "code": 200,  # 示例响应代码
            "sort": data.get("sort", 0),  # 传回接收到的sort值
            "msg": f"Processed message: {data.get('msg', '')}"  # 处理后的消息
        }

        # 发送处理结果到服务器
        await send_json_message(websocket, **response)

    except json.JSONDecodeError:
        print("Received a message that is not valid JSON")
    except Exception as e:
        print(f"An error occurred during processing: {e}")


async def listen_to_server():
    # uri = "ws://localhost:8200/websocket/2023114271/1820005988631097345/00000_用户_田"
    uri = "ws://localhost:8200/websocket/1820005988618514433/1820005988631097345/00001_用户_田"  # 替换为你的WebSocket服务器的URL

    async with websockets.connect(uri) as websocket:
        print("Connected to server")

        # 向服务器发送初始消息
        await send_json_message(websocket, code=1, sort=2, msg="dda")

        while True:
            try:
                # 等待并接收来自服务器的消息
                message = await websocket.recv()

                print(f"Received message: {message}")

                # 处理消息并响应
                await process_and_respond(websocket, message)

            except websockets.ConnectionClosed:
                print("Connection closed")
                break

            except Exception as e:
                print(f"An error occurred: {e}")
                break


# 启动事件循环并运行客户端
asyncio.get_event_loop().run_until_complete(listen_to_server())
