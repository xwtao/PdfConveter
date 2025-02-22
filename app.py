from flask import Flask, request, jsonify, send_file, render_template
from werkzeug.utils import secure_filename
import os
from pdf2docx import Converter
import time
from flask import after_this_request
import json
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max-limit
app.config['STATS_FILE'] = 'stats.json'

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def load_stats():
    """加载统计数据"""
    if os.path.exists(app.config['STATS_FILE']):
        try:
            with open(app.config['STATS_FILE'], 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            app.logger.error(f"Error loading stats: {e}")
    return {"total_requests": 0, "success_count": 0, "fail_count": 0, "requests": []}

def save_stats(stats):
    """保存统计数据"""
    try:
        with open(app.config['STATS_FILE'], 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
    except Exception as e:
        app.logger.error(f"Error saving stats: {e}")

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

@app.route('/')
def index():
    stats = load_stats()
    return render_template('index.html', stats=stats)

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
        'recent_requests': stats['requests'][:5]  # 只返回最近5条记录
    })

@app.route('/convert', methods=['POST'])
def convert():
    if 'file' not in request.files:
        update_stats(None, False, '未选择文件')
        return jsonify({'error': '未选择文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        update_stats(None, False, '未选择文件')
        return jsonify({'error': '未选择文件'}), 400

    try:
        # 原有的转换逻辑
        # ...
        update_stats(file.filename, True)
        return send_file(...)
    except Exception as e:
        error_msg = str(e)
        update_stats(file.filename, False, error_msg)
        return jsonify({'error': error_msg}), 500 