from flask import Flask
from flask import render_template, request, send_file, flash, after_this_request
import os
import shutil
from werkzeug.utils import secure_filename
from pdf2docx import Converter
import time
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = os.path.abspath(os.path.join(os.path.dirname(__file__), 'uploads'))
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max-limit
app.config['STATS_FILE'] = os.path.join(os.path.dirname(__file__), 'stats.json')

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'pdf'}

def load_stats():
    """加载统计数据"""
    if os.path.exists(app.config['STATS_FILE']):
        try:
            with open(app.config['STATS_FILE'], 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading stats: {e}")
    return {"total_requests": 0, "success_count": 0, "fail_count": 0, "requests": []}

def save_stats(stats):
    """保存统计数据"""
    try:
        with open(app.config['STATS_FILE'], 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving stats: {e}")

def update_stats(filename, success, error_msg=None):
    """更新统计数据"""
    stats = load_stats()
    stats["total_requests"] += 1
    if success:
        stats["success_count"] = stats.get("success_count", 0) + 1
    else:
        stats["fail_count"] = stats.get("fail_count", 0) + 1

    request_info = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "filename": filename,
        "success": success,
        "ip": request.remote_addr
    }
    if error_msg:
        request_info["error"] = error_msg
    stats["requests"].insert(0, request_info)  # 新记录插入到开头
    stats["requests"] = stats["requests"][:50]  # 只保留最近50条记录
    save_stats(stats)
    return stats

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def safe_remove_file(file_path):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"清理文件失败: {str(e)}")

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('没有选择文件')
            return render_template('convert.html', stats=load_stats())
        
        file = request.files['file']
        if file.filename == '':
            flash('没有选择文件')
            return render_template('convert.html', stats=load_stats())
        
        if file and allowed_file(file.filename):
            try:
                filename = secure_filename(file.filename)
                timestamp = str(int(time.time()))
                pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{timestamp}_{filename}")
                docx_path = os.path.join(app.config['UPLOAD_FOLDER'], 
                                       f"{timestamp}_{os.path.splitext(filename)[0]}.docx")
                temp_docx = os.path.join(app.config['UPLOAD_FOLDER'], 
                                       f"temp_{timestamp}_{os.path.splitext(filename)[0]}.docx")
                
                # 保存PDF文件
                file.save(pdf_path)
                
                try:
                    # 转换PDF到Word
                    cv = Converter(pdf_path)
                    cv.convert(docx_path)
                    cv.close()
                    
                    # 复制到临时文件
                    shutil.copy2(docx_path, temp_docx)
                    
                    # 清理原始文件
                    safe_remove_file(pdf_path)
                    safe_remove_file(docx_path)
                    
                    # 更新统计信息
                    update_stats(filename, True)
                    
                    @after_this_request
                    def remove_file(response):
                        safe_remove_file(temp_docx)
                        return response
                    
                    return send_file(
                        temp_docx,
                        as_attachment=True,
                        download_name=f"{os.path.splitext(filename)[0]}.docx"
                    )
                except Exception as e:
                    safe_remove_file(pdf_path)
                    safe_remove_file(docx_path)
                    safe_remove_file(temp_docx)
                    error_msg = str(e)
                    update_stats(filename, False, error_msg)
                    flash(f'转换失败：{error_msg}')
                    return render_template('convert.html', stats=load_stats())
            except Exception as e:
                error_msg = str(e)
                update_stats(filename, False, error_msg)
                flash(f'文件处理失败：{error_msg}')
                return render_template('convert.html', stats=load_stats())
        else:
            flash('不支持的文件格式，请上传PDF文件')
            return render_template('convert.html', stats=load_stats())
            
    return render_template('convert.html', stats=load_stats())

if __name__ == '__main__':
    app.run(debug=True) 