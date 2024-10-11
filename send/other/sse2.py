# 导入所需的模块
import json
import time
import datetime
from flask import Flask, request, Response, render_template

app = Flask(__name__)

# 解决跨域问题
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

# 获取当前时间，并转换为 JSON 格式
def get_time_json():
    dt_ms = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    return json.dumps({'time': dt_ms}, ensure_ascii=False)

# 设置路由，返回 SSE 流
@app.route('/')
def hello_world():
    return render_template('sse.html')

@app.route('/sse')
def stream():
    user_id = request.args.get('user_id')  # 可选，用于区分不同用户的连接
    print(user_id)

    def eventStream():
        id = 0
        while True:
            id += 1
            time.sleep(1/50)  # 50Hz，每秒发送约 50 条数据
            event_name = 'time_reading'
            str_out = f'id: {id}\nevent: {event_name}\ndata: {get_time_json()}\n\n'
            print(str_out)  # 在服务器端打印发送的数据
            yield str_out

    return Response(eventStream(), mimetype="text/event-stream")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5678, debug=True)