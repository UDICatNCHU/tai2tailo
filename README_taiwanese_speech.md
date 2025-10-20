# 台語語音轉台羅文字系統

使用 Claude 多模態 API 將台語語音檔案轉換為台羅拼音文字。

## 安裝步驟

1. 安裝 Python 套件：
```bash
pip install -r requirements.txt
```

2. 設定 Anthropic API 金鑰：
```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

## 使用方式

### 基本使用

```bash
python taiwanese_speech_to_tailo.py <音訊檔案路徑>
```

### 範例

```bash
# 使用 WAV 檔案
python taiwanese_speech_to_tailo.py recording.wav

# 使用 MP3 檔案
python taiwanese_speech_to_tailo.py taiwanese_audio.mp3
```

### 在程式中使用

```python
from taiwanese_speech_to_tailo import taiwanese_speech_to_tailo

# 轉換語音檔
result = taiwanese_speech_to_tailo("path/to/audio.wav")
print(result)

# 或者指定 API 金鑰
result = taiwanese_speech_to_tailo("audio.wav", api_key="your-key")
```

## 支援的音訊格式

- WAV (.wav)
- MP3 (.mp3)
- MP4/M4A (.mp4, .m4a)
- OGG (.ogg)
- FLAC (.flac)
- WEBM (.webm)

## 輸出

程式會：
1. 在終端機顯示台羅拼音結果
2. 自動將結果儲存到 `<原檔名>_tailo.txt` 檔案

## 台羅拼音說明

台羅拼音（Tâi-lô）是台語羅馬字拼音系統，包含聲調符號：
- 第二聲：á（高升）
- 第三聲：à（低降）
- 第五聲：â（高降）
- 第七聲：ā（中平）
- 第八聲：a̍h（高入）

## 注意事項

- 確保音訊檔案清晰，背景噪音會影響辨識準確度
- Claude 的語音辨識能力依賴於訓練資料，台語辨識可能需要多次調整
- API 使用會產生費用，請參考 Anthropic 定價
