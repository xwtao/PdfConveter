from flask import Flask
from flask import render_template, request, send_file, flash, after_this_request
import os
import shutil
from werkzeug.utils import secure_filename
from pdf2docx import Converter
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = os.path.abspath(os.path.join(os.path.dirname(__file__), 'uploads'))
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max-limit

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'pdf'}

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
            return render_template('index.html')
        
        file = request.files['file']
        if file.filename == '':
            flash('没有选择文件')
            return render_template('index.html')
        
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
                    flash(f'转换失败：{str(e)}')
                    return render_template('index.html')
            except Exception as e:
                flash(f'文件处理失败：{str(e)}')
                return render_template('index.html')
        else:
            flash('不支持的文件格式，请上传PDF文件')
            return render_template('index.html')
            
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True) 