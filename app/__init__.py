from flask import Flask, request, jsonify, send_file, render_template, redirect, url_for, flash, after_this_request
import os
import shutil
from werkzeug.utils import secure_filename
from pdf2docx import Converter
import time
import json
import logging
import threading
import glob
from datetime import datetime, timedelta
import pytz
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import hashlib
from urllib.parse import quote
from werkzeug.datastructures import Headers

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 设置时区为北京时间
beijing_tz = pytz.timezone('Asia/Shanghai')

def create_app():
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    
    # 确保必要的文件存在
    stats_file = os.path.join(app.root_path, 'stats.json')
    feedback_file = os.path.join(app.root_path, 'feedback.json')
    
    if not os.path.exists(stats_file):
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump({
                "total_requests": 0,
                "success_count": 0,
                "fail_count": 0,
                "requests": []
            }, f, ensure_ascii=False, indent=2)
    
    if not os.path.exists(feedback_file):
        with open(feedback_file, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
    
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    app.config['UPLOAD_FOLDER'] = os.path.abspath(os.path.join(os.path.dirname(__file__), 'uploads'))
    app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max-limit
    app.config['STATS_FILE'] = stats_file
    app.config['FEEDBACK_FILE'] = feedback_file
    app.config['VERSION'] = '1.0.2'  # 添加版本号配置

    # 邮件配置
    app.config['MAIL_ENABLED'] = True  # 是否启用邮件通知
    app.config['MAIL_SERVER'] = 'smtp.163.com'  # 网易邮箱服务器
    app.config['MAIL_PORT'] = 465  # 网易邮箱SSL端口
    app.config['MAIL_USE_SSL'] = True  # 使用SSL
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'xwt_1234@163.com')  # 从环境变量获取邮箱地址
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'RHjnD37NJvbenczd')  # 从环境变量获取授权码
    app.config['MAIL_DEFAULT_SENDER'] = 'xwt_1234@163.com'  # 发件人需要是完整的邮箱地址
    app.config['MAIL_ADMIN'] = os.environ.get('MAIL_ADMIN', 'xwtaos@163.com')  # 管理员邮箱

    # 确保必要的目录存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    logger.info(f"Upload directory created at: {os.path.abspath(app.config['UPLOAD_FOLDER'])}")
    logger.info(f"Template directory: {os.path.abspath('app/templates')}")

    ALLOWED_EXTENSIONS = {'pdf'}

    return app

app = create_app()

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
        "timestamp": datetime.now(beijing_tz).strftime("%Y-%m-%d %H:%M:%S"),
        "filename": filename,
        "success": success,
        "ip": request.remote_addr,
        "file_size": request.content_length
    }
    if error_msg:
        request_info["error"] = error_msg
    stats["requests"].insert(0, request_info)  # 新记录插入到开头
    stats["requests"] = stats["requests"][:50]  # 只保留最近50条记录
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

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def safe_remove_file(file_path, max_retries=3, delay=1):
    """安全删除文件，带重试机制"""
    for i in range(max_retries):
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.debug(f"Successfully removed file: {file_path}")
                return True
        except Exception as e:
            if i < max_retries - 1:
                logger.warning(f"Attempt {i+1} to remove file failed: {e}")
                time.sleep(delay)
            else:
                logger.error(f"Failed to remove file after {max_retries} attempts: {e}")
    return False

def cleanup_uploads():
    """每5分钟清理一次uploads目录中的文件，只清理超过10分钟未访问的文件"""
    while True:
        try:
            time.sleep(300)  # 先等待5分钟再开始清理
            
            # 获取uploads目录下的所有文件
            files = glob.glob(os.path.join(app.config['UPLOAD_FOLDER'], '*'))
            current_time = time.time()
            
            for file_path in files:
                try:
                    if os.path.exists(file_path):
                        # 获取文件最后访问时间
                        last_access_time = os.path.getatime(file_path)
                        # 如果文件超过10分钟未访问，则尝试删除
                        if current_time - last_access_time > 600:  # 600秒 = 10分钟
                            if safe_remove_file(file_path):
                                logger.info(f"Cleaned up old file: {file_path}")
                except Exception as e:
                    logger.error(f"Error checking file {file_path}: {e}")
                    
        except Exception as e:
            logger.error(f"Error in cleanup thread: {e}")
            time.sleep(300)

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

    pdf_path = None
    docx_path = None
    
    try:
        # 保留原始文件名（用于生成下载时的文件名）
        original_filename = file.filename
        # 生成安全的文件名用于存储
        safe_filename = secure_filename(original_filename)
        short_hash = generate_short_hash(safe_filename)
        
        # 使用短哈希值作为文件名
        filename = f"{short_hash}.pdf"
        docx_filename = f"{short_hash}.docx"
        # 生成下载时显示的文件名（保留原始文件名）
        display_filename = os.path.splitext(original_filename)[0] + '.docx'
        
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
        safe_remove_file(pdf_path)
        logger.debug("Removed original PDF file")
        
        # 更新统计信息，使用短哈希值作为文件名
        update_stats(short_hash, True)
        logger.info("Conversion successful")

        try:
            # 使用send_file发送文件
            response = send_file(
                docx_path,
                as_attachment=True,
                download_name=display_filename,
                mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )

            # 添加必要的响应头
            response.headers.add('Access-Control-Expose-Headers', 'Content-Disposition')
            response.headers.add('Cache-Control', 'no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0')
            response.headers.add('Pragma', 'no-cache')
            response.headers.add('Expires', '0')

            # 延迟删除文件
            def delayed_remove():
                time.sleep(5)  # 等待5秒后再删除
                safe_remove_file(docx_path)
                
            threading.Thread(target=delayed_remove, daemon=True).start()
            
            return response

        except Exception as e:
            logger.error(f"Error sending file: {e}")
            safe_remove_file(docx_path)
            return jsonify({'error': '文件下载失败，请重试'}), 500

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Conversion error: {error_msg}")
        # 清理可能存在的临时文件
        if pdf_path and os.path.exists(pdf_path):
            safe_remove_file(pdf_path)
        if docx_path and os.path.exists(docx_path):
            safe_remove_file(docx_path)
        # 使用短哈希值作为文件名记录失败
        update_stats(short_hash, False, error_msg)
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
        'timestamp': datetime.now(beijing_tz).strftime('%Y-%m-%d %H:%M:%S'),
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

# 启动清理线程
cleanup_thread = threading.Thread(target=cleanup_uploads, daemon=True)
cleanup_thread.start()
logger.info("Started uploads cleanup thread")

if __name__ == '__main__':
    # 设置最大内容长度为100MB
    app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
    # 运行应用
    app.run(
        host='127.0.0.1',  # 只监听本地连接
        port=5000,
        debug=True,
        threaded=True
    ) 