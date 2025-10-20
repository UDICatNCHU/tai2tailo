#!/usr/bin/env python3
"""
台語語音轉台羅文字
使用 OpenAI Whisper + GPT 進行語音辨識並轉換為台羅拼音
"""

import os
from pathlib import Path
from openai import OpenAI


def taiwanese_speech_to_tailo(audio_file_path, api_key=None):
    """
    將台語語音檔轉換為台羅拼音文字

    參數:
        audio_file_path: 音訊檔案路徑
        api_key: OpenAI API 金鑰（若未提供則從環境變數 OPENAI_API_KEY 讀取）

    返回:
        台羅拼音文字字串
    """
    # 檢查檔案是否存在
    if not os.path.exists(audio_file_path):
        raise FileNotFoundError(f"找不到音訊檔案: {audio_file_path}")

    # 初始化 OpenAI 客戶端
    if api_key is None:
        api_key = os.environ.get("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("請提供 OpenAI API 金鑰或設定 OPENAI_API_KEY 環境變數")

    client = OpenAI(api_key=api_key)

    # 步驟 1: 使用 Whisper 將音訊轉為文字
    print(f"正在讀取音訊檔案: {audio_file_path}")
    print("正在使用 Whisper 進行語音辨識...")

    with open(audio_file_path, 'rb') as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="zh"  # 指定為中文（包含閩南語）
        )

    chinese_text = transcription.text
    print(f"辨識的中文文字: {chinese_text}")

    # 步驟 2: 使用 GPT 將中文轉換為台羅拼音
    print("正在使用 GPT 轉換為台羅拼音...")

    response = client.chat.completions.create(
        model="gpt-4o",  # 使用 GPT-4o 模型
        messages=[
            {
                "role": "system",
                "content": "你是一個台語專家，精通台羅拼音（Tâi-lô romanization）標記系統。"
            },
            {
                "role": "user",
                "content": f"""這是一段台語（閩南語）的中文轉寫：

「{chinese_text}」

請將這段台語文字轉換為台羅拼音（Tâi-lô romanization）。

要求：
1. 這是台語/閩南語，不是華語
2. 請使用台羅拼音系統（Tâi-lô romanization）來標記
3. 保留聲調符號（如：â, é, ǹg 等）
4. 如果不確定某些詞彙，請提供最接近的台羅拼音
5. 只輸出台羅拼音文字，不需要其他說明

範例格式：
Guá sī lâng. (我是人)
Lí hó! (你好)"""
            }
        ],
        temperature=0.3,
        max_tokens=2000
    )

    # 提取回應文字
    tailo_text = response.choices[0].message.content

    print("\n=== 辨識完成 ===")
    return tailo_text


def main():
    """主程式"""
    import sys

    # 檢查命令列參數
    if len(sys.argv) < 2:
        print("使用方式: python taiwanese_speech_to_tailo.py <音訊檔案路徑>")
        print("支援格式: WAV, MP3, MP4, M4A, OGG, FLAC, WEBM")
        print("\n範例:")
        print("  python taiwanese_speech_to_tailo.py recording.wav")
        print("  python taiwanese_speech_to_tailo.py /path/to/taiwanese_audio.mp3")
        sys.exit(1)

    audio_path = sys.argv[1]

    try:
        # 執行語音轉文字
        result = taiwanese_speech_to_tailo(audio_path)

        print("\n台羅拼音結果:")
        print("=" * 50)
        print(result)
        print("=" * 50)

        # 選擇性：儲存結果到檔案
        output_file = Path(audio_path).stem + "_tailo.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result)
        print(f"\n結果已儲存至: {output_file}")

    except Exception as e:
        print(f"錯誤: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
