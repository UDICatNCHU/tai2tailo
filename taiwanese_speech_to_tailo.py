#!/usr/bin/env python3
"""
台語語音轉台羅拼音及中文翻譯
使用 OpenAI Whisper 進行語音辨識，直接輸出台羅拼音，並用 GPT 提供 Top-3 候選結果
然後利用台羅字典查詢每個詞彙的可能對應字詞，最後使用 LLM 生成最有可能的中文句子
"""

import os
import re
import json
from pathlib import Path
from openai import OpenAI
from tailo_dictionary import TailoDictionary


def taiwanese_speech_to_tailo(audio_file_path, api_key=None, dictionary_path="kautian.ods"):
    """
    將台語語音檔直接轉換為台羅拼音，並提供中文翻譯候選

    參數:
        audio_file_path: 音訊檔案路徑
        api_key: OpenAI API 金鑰（若未提供則從環境變數 OPENAI_API_KEY 讀取）
        dictionary_path: 台羅字典檔案路徑（預設為 "kautian.ods"）

    返回:
        包含台羅拼音候選結果及中文翻譯的字典
        {
            "tailo_candidates": Top-3 台羅拼音候選結果,
            "word_candidates": 每個台羅詞彙的可能對應字詞,
            "chinese_translation": LLM 生成的最有可能中文翻譯
        }
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

    print(f"正在讀取音訊檔案: {audio_file_path}")

    # 步驟 1a: 雙軌辨識 - 路徑1：Whisper 輸出中文
    print("\n=== 路徑 1: Whisper 辨識為中文 ===")

    with open(audio_file_path, 'rb') as audio_file:
        chinese_transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="zh",
            prompt="這是台語對話，請輸出中文。"
        )

    chinese_result = chinese_transcription.text
    print(f"中文辨識結果: {chinese_result}")

    # 步驟 1b: 雙軌辨識 - 路徑2：Whisper 輸出台羅拼音
    print("\n=== 路徑 2: Whisper 辨識為台羅拼音 ===")

    tailo_prompt = """台語台羅拼音對話。醫療詞彙範例：
    khuànn-pēⁿ 看病, khuànn i-sing 看醫生, i-sing-kuán 醫生館
    pak-tóo thiàⁿ 肚子痛, thâu-khak thiàⁿ 頭痛, huat-sio 發燒
    ka-sàu 咳嗽, kám-mōo 感冒, lâu-phīⁿ-tsuí 流鼻水
    tsia̍h-io̍h 吃藥, phah-tsiam 打針, khui-to 開刀
    """

    with open(audio_file_path, 'rb') as audio_file:
        tailo_transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="zh",
            prompt=tailo_prompt
        )

    tailo_result = tailo_transcription.text
    print(f"台羅辨識結果: {tailo_result}")

    # 步驟 2: 使用 GPT 生成標準台羅拼音（基於雙軌辨識結果）
    print("\n=== 步驟 2: 生成標準台羅拼音 ===")

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "你是一位台語專家，精通台羅拼音（Tâi-lô）標記系統和台語中文翻譯。"
            },
            {
                "role": "user",
                "content": f"""我有一段台語語音的兩種辨識結果：

**路徑 1 - 中文辨識**: {chinese_result}
**路徑 2 - 台羅辨識**: {tailo_result}

請根據這兩個結果，生成**最可能的標準台羅拼音（Tâi-lô）**。

**轉換要求**：
1. 輸出標準台羅拼音格式
2. 使用正確的聲調符號（â, á, à, ā, a̍h, ê, ó, ô͘, ǹg 等）
3. 詞與詞之間用空格分隔
4. 連字符用 - 連接（例如：khuànn-pēⁿ）
5. 參考兩個路徑的結果，選擇最合理的台羅拼音

請直接輸出台羅拼音，不需要其他解釋。"""
            }
        ],
        temperature=0.2,
        max_tokens=500
    )

    best_tailo = response.choices[0].message.content.strip()
    print(f"標準台羅拼音: {best_tailo}")

    # 步驟 3: 使用台羅字典查詢每個詞彙的可能對應字詞
    print("\n=== 步驟 3: 字典查詢與斷詞 ===")

    # 初始化字典（如果檔案存在）
    word_candidates_data = {}
    chinese_translation = ""

    if os.path.exists(dictionary_path):
        try:
            dictionary = TailoDictionary(dictionary_path)

            # 使用最大匹配算法進行字典查詢
            word_lookup_results = dictionary.segment_and_lookup(best_tailo, max_candidates=3, use_max_matching=True)

            print(f"斷詞結果: {[w['tailo'] for w in word_lookup_results]}")

            # 簡化格式，準備給前端和 LLM 使用
            word_candidates = []
            for word_result in word_lookup_results:
                options = []
                for c in word_result['candidates']:
                    # 處理 NaN 值
                    category = c['分類'] if c['分類'] == c['分類'] else None
                    options.append({
                        "chinese": c['漢字_清理'],
                        "romanization": c['羅馬字'],
                        "category": category
                    })

                word_candidates.append({
                    "tailo": word_result['tailo'],
                    "found": word_result['found'],
                    "options": options
                })

            word_candidates_data = {
                "tailo_input": best_tailo,
                "words": word_candidates
            }

            print(f"字典查詢完成，找到 {len(word_candidates)} 個詞彙")

            # 步驟 4: 使用 GPT 根據雙軌辨識 + 字典候選生成最終中文翻譯
            print("\n=== 步驟 4: 生成最終中文翻譯 ===")

            # 準備字典查詢結果參考文本
            reference_text = "【字典查詢結果】\n"
            for word_data in word_candidates:
                reference_text += f"\n台羅: {word_data['tailo']}\n"
                if word_data['options']:
                    reference_text += "可能的中文:\n"
                    for i, option in enumerate(word_data['options'][:3], 1):  # 最多 3 個
                        category_str = f" ({option['category']})" if option['category'] else ""
                        reference_text += f"  {i}. {option['chinese']}{category_str}\n"
                else:
                    reference_text += "  (查無對應)\n"

            translation_response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "你是一位台語專家，精通台語和中文翻譯。你需要綜合多種資訊來源，給出最準確的翻譯。"
                    },
                    {
                        "role": "user",
                        "content": f"""我有一段台語語音的多種辨識和分析結果，請你綜合這些資訊，給出**最準確的中文翻譯**。

【語音辨識結果】
- Whisper 中文辨識: {chinese_result}
- Whisper 台羅辨識: {tailo_result}
- 標準化台羅拼音: {best_tailo}

{reference_text}

**任務**：
請根據以上所有資訊，生成最準確、通順的中文翻譯。

**要求**：
1. 參考 Whisper 的中文辨識結果作為基礎
2. 使用字典查詢結果來修正可能的錯誤
3. 確保翻譯符合台語的語法和用詞習慣
4. 直接輸出中文翻譯，不需要解釋或分析

中文翻譯:"""
                    }
                ],
                temperature=0.2,
                max_tokens=500
            )

            chinese_translation = translation_response.choices[0].message.content.strip()
            print(f"中文翻譯: {chinese_translation}")

        except FileNotFoundError:
            print(f"字典檔案不存在: {dictionary_path}，跳過字典查詢")
        except Exception as e:
            print(f"字典查詢或翻譯時發生錯誤: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"字典檔案不存在: {dictionary_path}，跳過字典查詢")

    print("\n=== 辨識完成 ===")

    return {
        "chinese_result": chinese_result,  # Whisper 中文辨識
        "tailo_result": tailo_result,      # Whisper 台羅辨識
        "best_tailo": best_tailo,          # 標準化台羅拼音
        "word_candidates": word_candidates_data,  # 字典查詢結果
        "chinese_translation": chinese_translation  # 最終中文翻譯
    }


def main():
    """主程式"""
    import sys
    import json

    # 檢查命令列參數
    if len(sys.argv) < 2:
        print("使用方式: python taiwanese_speech_to_tailo.py <音訊檔案路徑>")
        print("支援格式: WAV, MP3, MP4, M4A, OGG, FLAC, WEBM")
        print()
        print("範例:")
        print("  python taiwanese_speech_to_tailo.py recording.wav")
        print("  python taiwanese_speech_to_tailo.py /path/to/audio.mp3")
        sys.exit(1)

    audio_path = sys.argv[1]

    try:
        # 執行語音轉台羅拼音
        result = taiwanese_speech_to_tailo(audio_path)

        print("\n" + "=" * 70)
        print("台羅拼音結果（Top 3）")
        print("=" * 70)
        for i, tailo in enumerate(result['tailo_candidates'], 1):
            print(f"{i}. {tailo}")
        print("=" * 70)

        # 儲存結果到檔案
        output_file = Path(audio_path).stem + "_tailo.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("台羅拼音候選結果（Top 3）:\n\n")
            for i, tailo in enumerate(result['tailo_candidates'], 1):
                f.write(f"{i}. {tailo}\n")
        print(f"\n結果已儲存至: {output_file}")

        # 同時儲存 JSON 格式
        json_file = Path(audio_path).stem + "_tailo.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"JSON 格式已儲存至: {json_file}")

    except Exception as e:
        print(f"錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
