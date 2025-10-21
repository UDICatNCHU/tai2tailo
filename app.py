#!/usr/bin/env python3
"""
台語醫療對談語音辨識 - 網頁版
簡單的 Flask 應用程式，提供網頁介面錄音並進行醫療對談辨識
"""

from flask import Flask, render_template, request, jsonify
from taiwanese_speech_to_tailo import taiwanese_speech_to_tailo
import os
from pathlib import Path
import uuid
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

app = Flask(__name__)

# 設定上傳資料夾
UPLOAD_FOLDER = Path('uploads')
UPLOAD_FOLDER.mkdir(exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def index():
    """首頁"""
    return render_template('index.html')


@app.route('/api/transcribe', methods=['POST'])
def transcribe():
    """處理音訊檔案並進行語音辨識與修正"""
    try:
        # 檢查是否有上傳檔案
        if 'audio' not in request.files:
            return jsonify({'error': '沒有上傳音訊檔案'}), 400

        audio_file = request.files['audio']

        if audio_file.filename == '':
            return jsonify({'error': '沒有選擇檔案'}), 400

        # 產生唯一檔名
        file_extension = '.webm'  # 瀏覽器錄音通常是 webm 格式
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = app.config['UPLOAD_FOLDER'] / unique_filename

        # 儲存上傳的檔案
        audio_file.save(file_path)

        # 執行語音辨識並轉換為台羅拼音
        result = taiwanese_speech_to_tailo(str(file_path))

        # 刪除暫存檔案
        try:
            os.remove(file_path)
        except:
            pass

        return jsonify({
            'success': True,
            'chinese_result': result.get('chinese_result', ''),  # Whisper 中文
            'tailo_result': result.get('tailo_result', ''),      # Whisper 台羅
            'best_tailo': result.get('best_tailo', ''),          # 標準台羅
            'word_candidates': result.get('word_candidates', {}),
            'chinese_translation': result.get('chinese_translation', '')  # 最終翻譯
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    print("=" * 60)
    print("台語語音辨識 - 網頁版")
    print("=" * 60)
    print("正在啟動網頁伺服器...")
    print("請在瀏覽器開啟: http://localhost:5001")
    print()
    print("功能:")
    print("  - Whisper 語音辨識")
    print("  - GPT 辨識錯誤修正")
    print()
    print("按 Ctrl+C 停止伺服器")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5001)
