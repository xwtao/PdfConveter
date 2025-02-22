from flask import Flask, request, jsonify, send_file, render_template, redirect, url_for
from werkzeug.utils import secure_filename
import os
import logging
from pdf2docx import Converter
import time
from flask import after_this_request
import json
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import hashlib
import threading
import glob

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__, 
    template_folder='templates',  # 指定模板目录
    static_folder='static'  # 指定静态文件目录
)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max-limit
app.config['STATS_FILE'] = 'stats.json'
app.config['FEEDBACK_FILE'] = 'feedback.json'
app.config['VERSION'] = '1.0.2'  # 添加版本号配置

# 邮件配置
app.config['MAIL_ENABLED'] = True  # 是否启用邮件通知
app.config['MAIL_SERVER'] = 'smtp.163.com'  # 网易邮箱服务器
app.config['MAIL_PORT'] = 465  # 网易邮箱SSL端口
app.config['MAIL_USE_SSL'] = True  # 使用SSL
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME','xwt_1234@163.com')  # 从环境变量获取邮箱地址
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD','RHjnD37NJvbenczd')  # 从环境变量获取授权码(不是邮箱密码)
app.config['MAIL_DEFAULT_SENDER'] = 'xwt_1234@163.com'  # 发件人需要是完整的邮箱地址
app.config['MAIL_ADMIN'] = os.environ.get('MAIL_ADMIN', 'xwtaos@163.com')  # 管理员邮箱

# 确保必要的目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('templates', exist_ok=True)
os.makedirs('static', exist_ok=True)
logger.info(f"Upload directory created at: {os.path.abspath(app.config['UPLOAD_FOLDER'])}")
logger.info(f"Template directory: {os.path.abspath('templates')}")

def load_stats():
    """加载统计数据"""
    if os.path.exists(app.config['STATS_FILE']):
        try:
            with open(app.config['STATS_FILE'], 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading stats: {e}")
    return {"total_requests": 0, "success_count": 0, "fail_count": 0, "requests": []}

def save_stats(stats):
    """保存统计数据"""
    try:
        with open(app.config['STATS_FILE'], 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error saving stats: {e}")

def update_stats(filename, success, error_msg=None):
    """更新统计数据"""
    stats = load_stats()
    stats["total_requests"] += 1
    if success:
        stats["success_count"] = stats.get("success_count", 0) + 1
    else:
        stats["fail_count"] = stats.get("fail_count", 0) + 1

    request_info = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "filename": filename,
        "success": success,
        "ip": request.remote_addr,
        "file_size": request.content_length
    }
    if error_msg:
        request_info["error"] = error_msg
    stats["requests"].insert(0, request_info)  # 新记录插入到开头
    # 只保留最近50条记录
    stats["requests"] = stats["requests"][:50]
    save_stats(stats)
    return stats

def load_feedback():
    """加载反馈数据"""
    if os.path.exists(app.config['FEEDBACK_FILE']):
        try:
            with open(app.config['FEEDBACK_FILE'], 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_feedback(feedback_list):
    """保存反馈数据"""
    try:
        with open(app.config['FEEDBACK_FILE'], 'w', encoding='utf-8') as f:
            json.dump(feedback_list, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error saving feedback: {e}")

def send_feedback_email(feedback):
    """发送反馈邮件通知"""
    if not app.config['MAIL_ENABLED'] or not app.config['MAIL_USERNAME'] or not app.config['MAIL_PASSWORD']:
        logger.warning("Mail notification is disabled or not configured")
        return

    try:
        msg = MIMEMultipart()
        msg['Subject'] = f"新的用户反馈 - {feedback['type']}"
        msg['From'] = app.config['MAIL_DEFAULT_SENDER']
        msg['To'] = app.config['MAIL_ADMIN']

        body = f"""
收到新的用户反馈：

类型：{feedback['type']}
内容：{feedback['content']}
联系方式：{feedback['contact']}
IP地址：{feedback['ip']}
时间：{feedback['timestamp']}
        """

        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        with smtplib.SMTP_SSL(app.config['MAIL_SERVER'], app.config['MAIL_PORT']) as server:
            server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            server.send_message(msg)
            
        logger.info("Feedback notification email sent successfully")
    except Exception as e:
        logger.error(f"Failed to send feedback notification email: {e}")

def generate_short_hash(filename):
    """生成文件名的短MD5值（前5位）"""
    return hashlib.md5(filename.encode()).hexdigest()[:5]

@app.route('/')
def redirect_to_version():
    return redirect(url_for('index_with_version', version=app.config['VERSION']))

@app.route('/v<version>')
def index_with_version(version):
    logger.debug(f"Accessing index page version {version}")
    stats = load_stats()
    return render_template('convert.html', stats=stats, version=version)

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/stats')
def get_stats():
    """获取统计信息"""
    stats = load_stats()
    return jsonify(stats)

@app.route('/stats/realtime')
def get_realtime_stats():
    """获取实时统计信息，用于前端轮询更新"""
    stats = load_stats()
    return jsonify({
        'total_requests': stats['total_requests'],
        'success_count': stats.get('success_count', 0),
        'fail_count': stats.get('fail_count', 0),
        'recent_requests': stats['requests'][:10]  # 显示最近10条记录
    })

@app.route('/convert', methods=['POST'])
def convert():
    logger.debug("Starting file conversion")
    if 'file' not in request.files:
        logger.warning("No file part in request")
        update_stats(None, False, '未选择文件')
        return jsonify({'error': '未选择文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        logger.warning("No selected file")
        update_stats(None, False, '未选择文件')
        return jsonify({'error': '未选择文件'}), 400

    try:
        original_filename = secure_filename(file.filename)
        short_hash = generate_short_hash(original_filename)
        
        # 使用短哈希值作为文件名
        filename = f"{short_hash}.pdf"
        docx_filename = f"{short_hash}.docx"
        
        logger.info(f"Processing file: {filename}")
        
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        docx_path = os.path.join(app.config['UPLOAD_FOLDER'], docx_filename)
        
        logger.debug(f"Saving PDF to: {pdf_path}")
        file.save(pdf_path)
        
        logger.debug("Starting PDF to DOCX conversion")
        cv = Converter(pdf_path)
        cv.convert(docx_path)
        cv.close()
        
        logger.debug("Conversion completed")
        
        # 删除PDF文件
        os.remove(pdf_path)
        logger.debug("Removed original PDF file")
        
        @after_this_request
        def remove_docx(response):
            try:
                if os.path.exists(docx_path):
                    os.remove(docx_path)
                    logger.debug("Removed converted DOCX file")
            except Exception as e:
                logger.error(f"Error removing DOCX file: {e}")
            return response
        
        # 更新统计信息，使用短哈希值作为文件名
        update_stats(short_hash, True)
        logger.info("Conversion successful")
        
        # 返回转换后的文件
        return send_file(
            docx_path,
            as_attachment=True,
            download_name=docx_filename,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Conversion error: {error_msg}")
        # 清理可能存在的临时文件
        for path in [pdf_path, docx_path]:
            try:
                if os.path.exists(path):
                    os.remove(path)
                    logger.debug(f"Cleaned up file: {path}")
            except:
                pass
        update_stats(file.filename, False, error_msg)
        return jsonify({'error': error_msg}), 500

@app.route('/feedback', methods=['POST'])
def submit_feedback():
    """提交反馈"""
    data = request.get_json()
    if not data or 'type' not in data or 'content' not in data:
        return jsonify({'error': '无效的反馈数据'}), 400

    feedback = {
        'type': data['type'],  # 'suggestion' 或 'bug'
        'content': data['content'],
        'contact': data.get('contact', ''),  # 可选的联系方式
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'ip': request.remote_addr
    }

    # 保存到文件
    feedback_list = load_feedback()
    feedback_list.insert(0, feedback)
    feedback_list = feedback_list[:1000]  # 只保留最近1000条反馈
    save_feedback(feedback_list)

    # 发送邮件通知
    send_feedback_email(feedback)

    return jsonify({'message': '感谢您的反馈！'})

def cleanup_uploads():
    """每5分钟清理一次uploads目录中的文件，只清理超过5分钟未访问的文件"""
    while True:
        try:
            # 获取uploads目录下的所有文件
            files = glob.glob(os.path.join(app.config['UPLOAD_FOLDER'], '*'))
            current_time = time.time()
            
            # 删除超过5分钟未访问的文件
            for file_path in files:
                try:
                    if os.path.exists(file_path):
                        # 获取文件最后访问时间
                        last_access_time = os.path.getatime(file_path)
                        # 如果文件超过5分钟未访问，则删除
                        if current_time - last_access_time > 300:  # 300秒 = 5分钟
                            os.remove(file_path)
                            logger.info(f"Cleaned up file: {file_path} (last accessed: {datetime.fromtimestamp(last_access_time)})")
                except Exception as e:
                    logger.error(f"Error cleaning up file {file_path}: {e}")
            
            # 每5分钟执行一次
            time.sleep(300)
        except Exception as e:
            logger.error(f"Error in cleanup thread: {e}")
            time.sleep(300)  # 发生错误时也等待5分钟后继续

@app.after_request
def add_header(response):
    """添加响应头以防止缓存"""
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, proxy-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

if __name__ == '__main__':
    # 启动清理线程
    cleanup_thread = threading.Thread(target=cleanup_uploads, daemon=True)
    cleanup_thread.start()
    logger.info("Started uploads cleanup thread")
    
    # 设置最大内容长度为100MB
    app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
    # 运行应用
    app.run(
        host='127.0.0.1',  # 只监听本地连接
        port=5000,
        debug=True,
        threaded=True
    ) 