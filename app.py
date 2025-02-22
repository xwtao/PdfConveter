from flask import jsonify

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"}), 200 