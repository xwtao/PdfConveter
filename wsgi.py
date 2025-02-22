from app import app
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.serving import WSGIRequestHandler

# 设置请求处理器以支持大文件上传
class CustomWSGIRequestHandler(WSGIRequestHandler):
    protocol_version = "HTTP/1.1"
    max_content_length = 10 * 1024 * 1024  # 10MB

# 应用ProxyFix中间件
app.wsgi_app = ProxyFix(
    app.wsgi_app, 
    x_for=1, 
    x_proto=1, 
    x_host=1, 
    x_port=1
)

# 确保模板目录存在
import os
if not os.path.exists('templates'):
    os.makedirs('templates')

if __name__ == "__main__":
    # 设置最大内容长度为10MB
    app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
    # 运行应用
    app.run(
        host='0.0.0.0',
        port=8080,
        debug=True,
        threaded=True,
        request_handler=CustomWSGIRequestHandler
    ) 