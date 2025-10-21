# 台羅字典查詢模組使用說明

## 概述

`tailo_dictionary.py` 提供台羅文字與中文的翻譯對照查詢功能，基於 `kautian.ods` 字典檔案（包含 29,152 筆詞彙資料）。

## 安裝相依套件

```bash
pip3 install odfpy pandas
```

## 快速開始

### 方法 1: Python 程式中使用

```python
from tailo_dictionary import TailoDictionary

# 初始化字典
dictionary = TailoDictionary("kautian.ods")

# 1. 單詞查詢
results = dictionary.lookup("lâng")
print(results[0]['漢字'])  # 輸出: 人

# 2. 翻譯句子
translation = dictionary.translate_sentence("guá ài lí")
print(translation)  # 輸出: 我愛你（可能因同音字而有不同結果）

# 3. 翻譯詞組
translation = dictionary.translate_sentence("it-to-lióng-tuān")
print(translation)  # 輸出: 一刀兩斷

# 4. 模糊搜尋
results = dictionary.fuzzy_search("hó", max_results=5)
for r in results:
    print(f"{r['漢字']} ({r['羅馬字']})")
```

### 方法 2: 命令列使用

#### 單詞查詢
```bash
python3 tailo_dictionary.py "lâng"
```

#### 互動模式
```bash
python3 tailo_dictionary.py
```

進入互動模式後，可使用以下指令：
- `lookup <台羅文字>` - 精確查詢
- `translate <台羅句子>` - 翻譯整句
- `search <台羅片段>` - 模糊搜尋
- `quit` - 離開

## API 說明

### TailoDictionary 類別

#### `__init__(ods_file_path="kautian.ods")`
初始化字典，載入 ODS 檔案。

**參數:**
- `ods_file_path`: 字典檔案路徑（預設: "kautian.ods"）

---

#### `lookup(tailo_text: str) -> List[Dict]`
精確查詢台羅文字對應的中文。

**參數:**
- `tailo_text`: 台羅文字

**返回:** 符合結果的列表，每個結果包含：
- `漢字`: 對應的中文
- `羅馬字`: 完整的台羅拼音
- `分類`: 詞彙分類
- `詞目類型`: 主詞目或又音

**範例:**
```python
results = dictionary.lookup("tsi̍t")
# 返回: [{'漢字': '一【替】', '羅馬字': 'tsi̍t', ...}]
```

---

#### `translate_sentence(tailo_sentence: str, show_details=False) -> str`
翻譯一整串台羅文字為中文。

**參數:**
- `tailo_sentence`: 台羅拼音句子（詞彙間以空格分隔）
- `show_details`: 是否顯示詳細的查詢資訊

**返回:** 翻譯後的中文文字

**範例:**
```python
translation = dictionary.translate_sentence("guá ài lí", show_details=True)
# 輸出會包含詳細的詞彙對照資訊
```

---

#### `fuzzy_search(tailo_text: str, max_results=10) -> List[Dict]`
模糊搜尋包含指定台羅片段的詞彙。

**參數:**
- `tailo_text`: 台羅文字片段
- `max_results`: 最多返回的結果數量

**返回:** 符合結果的列表

**範例:**
```python
results = dictionary.fuzzy_search("lâng", max_results=5)
# 返回所有包含 "lâng" 的詞彙
```

## 注意事項

1. **同音字問題**: 台語有許多同音字，`translate_sentence()` 會選擇字典中第一個符合的結果，可能不是最準確的翻譯。建議搭配 `show_details=True` 查看詳細資訊。

2. **詞彙標記**: 字典中有些詞彙帶有標記如【白】（白話音）、【文】（文讀音）、【替】（替用字），查詢時會自動處理這些標記。

3. **大小寫**: 查詢時會自動轉換為小寫，因此 "Guá" 和 "guá" 視為相同。

4. **詞組查詢**: 建議使用連字符（-）連接的詞組整體查詢，例如 "it-to-lióng-tuān" 會比分開查詢更準確。

## 使用範例

```python
from tailo_dictionary import TailoDictionary

# 初始化
dictionary = TailoDictionary()

# 範例 1: 查詢基本詞彙
print(dictionary.lookup("lâng"))
# 輸出: [{'漢字': '人【替】', '羅馬字': 'lâng', ...}]

# 範例 2: 翻譯詞組
print(dictionary.translate_sentence("it-to-lióng-tuān"))
# 輸出: 一刀兩斷

# 範例 3: 帶詳細資訊的翻譯
print(dictionary.translate_sentence("guá ài lí", show_details=True))
# 輸出:
# 我愛女
# 
# 詳細查詢:
# guá -> 我 (【白】guá)
# ài -> 愛 (ài)
# lí -> 女 (【白】lí/lú)

# 範例 4: 搜尋相關詞彙
results = dictionary.fuzzy_search("好")
for r in results[:5]:
    print(f"{r['漢字']} ({r['羅馬字']})")
```

## 字典資料來源

字典資料來自 `kautian.ods` 檔案，包含以下欄位：
- 詞目id
- 詞目類型
- 漢字
- 羅馬字
- 分類
- 羅馬字音檔檔名

總計 29,152 筆詞彙資料。
