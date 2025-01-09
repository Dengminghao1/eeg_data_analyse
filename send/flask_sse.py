import json
import time
from datetime import datetime, timedelta

from flask import Flask, Response

from Eeg.utils import calculate_cognitive, test_start_time, test_end_time, trans_to_json

# start_time = (datetime.now() - timedelta(seconds=9)).strftime('%Y-%m-%d %H:%M:%S')
# end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
app = Flask(__name__)



# 解决跨域问题
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


# def event_stream():
#     while True:
#         # 模拟从数据库或其他来源获取数据
#         # message = calculate_cognitive()
#         # message_str = str(message)
#
#         a, b = calculate_cognitive(test_start_time, test_end_time)
#         message = trans_to_json(a, b)
#         print(f"Sending message: {message}")
#         yield f"data: {message}\n\n"
#         time.sleep(5)  # 每5秒发送一次消息
#
# @app.route('/sse')
# def stream():
#     return Response(event_stream(), mimetype="text/event-stream")


# 处理带有变量的 SSE 路由
@app.route('/sse/<string:student_id>')
def sse_request(student_id):
    def generate():
        while True:
            # start_time = (datetime.now() - timedelta(seconds=9)).strftime('%Y-%m-%d %H:%M:%S')
            # end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            start_time = test_start_time
            end_time = test_end_time
            a, b = calculate_cognitive(start_time, end_time)
            message = trans_to_json(a, b)

            print(f"Sending message: student_id: {student_id}, message:{message}")
            yield f"data: {json.dumps(message)}\n\n"
            time.sleep(5)  # 每5秒发送一次消息


    # 设置响应头，Content-Type 必须是 text/event-stream
    return Response(generate(), mimetype='text/event-stream')


@app.route('/')
def index():
    return "测试发送消息是否成功，url后面+/sse"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    # app.run(debug=True)
