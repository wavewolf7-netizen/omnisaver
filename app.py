import os
from flask import Flask, render_template, request, jsonify, send_from_directory, abort
from downloader import extract_media_info, download_media, DOWNLOAD_DIR, clean_old_files, detect_platform

app = Flask(__name__)
app.config['SECRET_KEY'] = 'media-downloader-secret-2024'
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32 MB max payload

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/detect', methods=['POST'])
def api_detect():
    data = request.get_json(silent=True) or {}
    url = data.get('url', '').strip()
    platform = detect_platform(url)
    return jsonify({'platform': platform})

@app.route('/api/info', methods=['POST'])
def api_info():
    data = request.get_json(silent=True) or {}
    url = data.get('url', '').strip()
    if not url:
        return jsonify({'success': False, 'error': 'Please paste a valid video or reel link.'}), 400

    try:
        info = extract_media_info(url)
        return jsonify({'success': True, 'data': info})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/download', methods=['POST'])
def api_download():
    data = request.get_json(silent=True) or {}
    url = data.get('url', '').strip()
    format_type = data.get('format', 'video').strip().lower()

    if not url:
        return jsonify({'success': False, 'error': 'Please paste a valid link.'}), 400

    if format_type not in ['video', 'audio']:
        format_type = 'video'

    try:
        result = download_media(url, format_type=format_type)
        return jsonify({
            'success': True,
            'data': {
                'download_id': result['download_id'],
                'suggested_filename': result['suggested_filename'],
                'format': result['format'],
                'platform': result['platform'],
                'platform_name': result['platform_name'],
                'platform_badge': result['platform_badge'],
                'file_size_mb': result['file_size_mb'],
                'title': result['title'],
                'uploader': result['uploader'],
                'download_url': f"/download/file/{result['download_id']}?name={result['suggested_filename']}",
                'preview_url': f"/preview/file/{result['download_id']}"
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/download/file/<filename>')
def download_file(filename):
    safe_filename = os.path.basename(filename)
    file_path = os.path.join(DOWNLOAD_DIR, safe_filename)
    if not os.path.exists(file_path):
        abort(404, description="File has expired or was removed.")

    custom_name = request.args.get('name', safe_filename)
    return send_from_directory(
        DOWNLOAD_DIR,
        safe_filename,
        as_attachment=True,
        download_name=custom_name
    )

@app.route('/preview/file/<filename>')
def preview_file(filename):
    safe_filename = os.path.basename(filename)
    file_path = os.path.join(DOWNLOAD_DIR, safe_filename)
    if not os.path.exists(file_path):
        abort(404, description="Media file not found.")

    return send_from_directory(DOWNLOAD_DIR, safe_filename, as_attachment=False)

if __name__ == '__main__':
    clean_old_files()
    print("=" * 65)
    print(" 🚀 Universal Media Downloader (Instagram, YouTube, Facebook)")
    print(" 🌐 Access web UI at: http://127.0.0.1:5000")
    print("=" * 65)
    app.run(host='127.0.0.1', port=5000, debug=True)
