# 台語語音轉台羅拼音 (Taiwanese Speech to Tâi-lô)

一個使用 OpenAI Whisper 和 GPT 的台語語音轉台羅拼音工具，提供命令列和網頁介面兩種使用方式。

## 功能特色

- 🎤 **語音辨識**：使用 OpenAI Whisper 進行台語語音辨識
- 📝 **台羅轉換**：使用 GPT-4o 將中文轉換為台羅拼音（Tâi-lô romanization）
- 🌐 **網頁介面**：提供美觀的網頁錄音介面
- 💻 **命令列工具**：支援批次處理音訊檔案
- 🎵 **多格式支援**：支援 WAV, MP3, MP4, M4A, OGG, FLAC, WEBM 等格式

## 安裝說明

### 1. 複製專案

```bash
git clone <repository-url>
cd tai2tailo
```

### 2. 安裝相依套件

```bash
pip install -r requirements.txt
```

### 3. 設定 OpenAI API 金鑰

創建 `.env` 檔案並設定您的 OpenAI API 金鑰：

```env
OPENAI_API_KEY=your_openai_api_key_here
```

或者設定環境變數：

```bash
export OPENAI_API_KEY="your_openai_api_key_here"
```

## 使用方式

### 網頁版

1. 啟動網頁伺服器：
```bash
python app.py
```

2. 在瀏覽器開啟 `http://localhost:5001`

3. 點擊「開始錄音」按鈕開始錄製台語語音

4. 錄音完成後點擊「停止錄音」，系統會自動轉換為台羅拼音

### 命令列版

直接處理音訊檔案：

```bash
python taiwanese_speech_to_tailo.py <音訊檔案路徑>
```

範例：
```bash
python taiwanese_speech_to_tailo.py recording.wav
python taiwanese_speech_to_tailo.py /path/to/taiwanese_audio.mp3
```

## 專案結構

```
tai2tailo/
├── app.py                           # Flask 網頁應用程式
├── taiwanese_speech_to_tailo.py     # 核心轉換模組
├── requirements.txt                 # Python 相依套件
├── README.md                        # 專案說明文件
├── .env                            # 環境變數設定（需自行創建）
├── templates/
│   └── index.html                  # 網頁介面模板
├── uploads/                        # 暫存音訊檔案目錄
└── __pycache__/                    # Python 快取檔案
```

## 技術架構

### 語音辨識流程

1. **音訊輸入**：接收台語語音檔案或網頁錄音
2. **語音轉文字**：使用 OpenAI Whisper 模型進行語音辨識
3. **台羅轉換**：使用 GPT-4o 將中文轉換為台羅拼音
4. **結果輸出**：返回台羅拼音文字

### 使用的 API 和模型

- **OpenAI Whisper**：用於語音辨識，支援中文（包含閩南語）
- **GPT-4o**：用於中文到台羅拼音的轉換
- **Flask**：網頁應用程式框架

## 台羅拼音系統

本工具使用 **台羅拼音（Tâi-lô romanization）** 系統，這是台語羅馬字標準化方案。

### 特色：
- 保留聲調符號（如：â, é, ǹg 等）
- 符合教育部台語羅馬字拼音方案
- 適合學術研究和教學使用

### 範例：
- 「我是人」→ `Guá sī lâng.`
- 「你好」→ `Lí hó!`
- 「多謝」→ `To-siā`

## 網頁介面功能

- 🎨 **現代化設計**：美觀的漸層背景和卡片式設計
- 📱 **響應式介面**：支援各種螢幕尺寸
- 🎙️ **即時錄音**：瀏覽器內建錄音功能
- ⏱️ **錄音計時器**：顯示錄音時間
- 📋 **結果顯示**：清楚呈現轉換結果
- 📥 **結果下載**：可複製或下載轉換結果

## 系統需求

- Python 3.7 以上
- OpenAI API 金鑰
- 網路連線（用於 API 呼叫）
- 現代瀏覽器（支援 Web Audio API）

## 相依套件

```
openai>=1.0.0      # OpenAI API 客戶端
flask>=3.0.0       # 網頁框架
python-dotenv>=1.0.0  # 環境變數管理
```

## 常見問題

### Q: 為什麼需要 OpenAI API 金鑰？
A: 本工具使用 OpenAI 的 Whisper 和 GPT 服務進行語音辨識和台羅轉換，需要有效的 API 金鑰才能使用。

### Q: 支援哪些音訊格式？
A: 支援大部分常見格式：WAV, MP3, MP4, M4A, OGG, FLAC, WEBM 等。

### Q: 轉換準確度如何？
A: 準確度取決於：
- 語音清晰度
- 台語發音標準程度
- OpenAI 模型對台語的理解程度

### Q: 可以離線使用嗎？
A: 目前需要網路連線才能使用 OpenAI API，暫不支援離線模式。

## 注意事項

1. **API 費用**：使用 OpenAI API 會產生費用，請注意用量
2. **隱私保護**：音訊檔案會暫時上傳到 OpenAI 伺服器處理
3. **語言限制**：主要針對台語設計，其他語言效果可能不佳
4. **網路需求**：需要穩定的網路連線

## 授權條款

本專案採用 MIT 授權條款。

## 貢獻指南

歡迎提交 Issue 和 Pull Request 來改進此專案：

1. Fork 此專案
2. 創建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

## 聯絡資訊

如有問題或建議，歡迎透過 GitHub Issues 聯絡。

---

**台語文化保存，從數位工具開始 🇹🇼**
