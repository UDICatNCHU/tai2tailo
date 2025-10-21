#!/usr/bin/env python3
"""
台羅字典查詢模組
提供台羅文字到中文的翻譯對照查詢功能
"""

import pandas as pd
import re
from typing import Optional, List, Dict
from pathlib import Path


class TailoDictionary:
    """台羅字典類別，用於進行台羅與中文字詞的翻譯對照查詢"""

    def __init__(self, ods_file_path: str = "kautian.ods"):
        """
        初始化台羅字典

        參數:
            ods_file_path: ODS 字典檔案路徑，預設為 "kautian.ods"
        """
        self.ods_file_path = ods_file_path
        self.df = None
        self._load_dictionary()

    def _load_dictionary(self):
        """載入 ODS 字典檔案"""
        if not Path(self.ods_file_path).exists():
            raise FileNotFoundError(f"找不到字典檔案: {self.ods_file_path}")

        print(f"正在載入字典檔案: {self.ods_file_path}")
        self.df = pd.read_excel(self.ods_file_path, engine='odf')
        print(f"字典載入完成，共 {len(self.df)} 筆資料")

    def _normalize_tailo(self, text: str) -> str:
        """
        正規化台羅文字，用於比對
        - 移除空白
        - 轉換為小寫

        參數:
            text: 輸入的台羅文字

        返回:
            正規化後的文字
        """
        return text.strip().lower()

    def lookup(self, tailo_text: str) -> List[Dict]:
        """
        查詢台羅文字對應的中文

        參數:
            tailo_text: 台羅文字（可包含多個音讀，用 / 分隔）

        返回:
            符合的結果列表，每個結果為字典，包含:
            - 漢字: 對應的中文
            - 羅馬字: 完整的台羅拼音
            - 分類: 詞彙分類
            - 詞目類型: 主詞目或又音
        """
        normalized_input = self._normalize_tailo(tailo_text)
        results = []

        # 在羅馬字欄位中搜尋
        for idx, row in self.df.iterrows():
            roma_text = str(row['羅馬字'])

            # 移除【文】【白】等標記
            roma_text_clean = re.sub(r'【[^】]+】', '', roma_text)

            # 處理多個音讀的情況（用 / 分隔）
            roma_variants = [self._normalize_tailo(r.strip()) for r in roma_text_clean.split('/')]

            # 檢查是否有任何一個音讀符合
            if normalized_input in roma_variants:
                results.append({
                    '漢字': row['漢字'],
                    '羅馬字': row['羅馬字'],
                    '分類': row['分類'],
                    '詞目類型': row['詞目類型']
                })

        return results

    def segment_with_max_matching(self, tailo_sentence: str) -> List[str]:
        """
        使用最大匹配算法（貪婪法）進行台羅斷詞

        參數:
            tailo_sentence: 台羅拼音句子（可能有或沒有空格）

        返回:
            斷詞後的詞彙列表
        """
        # 先移除所有空格，重新斷詞
        text = tailo_sentence.replace(' ', '').replace('-', '')

        if not text:
            return []

        # 建立所有可能的台羅詞彙集合（從字典中提取）
        vocab_set = set()
        for idx, row in self.df.iterrows():
            roma_text = str(row['羅馬字'])
            # 移除標記和空格
            roma_clean = re.sub(r'【[^】]+】', '', roma_text)
            # 處理多個音讀
            for variant in roma_clean.split('/'):
                normalized = self._normalize_tailo(variant.strip().replace('-', ''))
                if normalized:
                    vocab_set.add(normalized)

        # 最大匹配算法（從左到右，貪婪匹配）
        result = []
        i = 0
        max_word_len = 20  # 假設最長詞不超過 20 個字符

        while i < len(text):
            # 從最長可能的詞開始嘗試
            matched = False
            for length in range(min(max_word_len, len(text) - i), 0, -1):
                word = text[i:i+length].lower()
                if word in vocab_set:
                    result.append(text[i:i+length])  # 保留原始大小寫
                    i += length
                    matched = True
                    break

            # 如果沒有匹配，單字符前進
            if not matched:
                # 嘗試找到下一個可能的起點（可能是聲調符號等）
                result.append(text[i])
                i += 1

        return result

    def segment_and_lookup(self, tailo_sentence: str, max_candidates: int = 5, use_max_matching: bool = True) -> List[Dict]:
        """
        斷詞並查詢每個詞的對應翻譯候選

        參數:
            tailo_sentence: 台羅拼音句子
            max_candidates: 每個詞最多返回的候選翻譯數量
            use_max_matching: 是否使用最大匹配算法斷詞（預設 True），否則以空格分隔

        返回:
            每個詞的查詢結果列表，格式:
            [
                {
                    'tailo': '原始台羅詞',
                    'candidates': [
                        {'漢字': '中文', '羅馬字': '完整拼音', '分類': '分類', '詞目類型': '類型'},
                        ...
                    ],
                    'found': True/False
                },
                ...
            ]
        """
        # 選擇斷詞方式
        if use_max_matching:
            words = self.segment_with_max_matching(tailo_sentence)
        else:
            words = tailo_sentence.split()

        results = []

        for word in words:
            # 跳過空字串或單字符（可能是斷詞失敗的字符）
            if not word or word.strip() == '' or len(word) == 1:
                continue

            # 查詢字典
            lookup_results = self.lookup(word)

            # 限制候選數量
            candidates = lookup_results[:max_candidates] if lookup_results else []

            # 清理漢字中的標記
            for candidate in candidates:
                candidate['漢字_清理'] = re.sub(r'【.*?】', '', candidate['漢字'])

            results.append({
                'tailo': word,
                'candidates': candidates,
                'found': len(candidates) > 0
            })

        return results

    def translate_sentence(self, tailo_sentence: str, show_details: bool = False) -> str:
        """
        翻譯一整串台羅文字為中文（保留此方法以向後兼容）

        參數:
            tailo_sentence: 台羅拼音句子（詞彙間以空格分隔）
            show_details: 是否顯示詳細的查詢資訊

        返回:
            翻譯後的中文文字（若無法完全翻譯則返回原文和找到的翻譯）
        """
        # 先嘗試整句查詢
        whole_results = self.lookup(tailo_sentence)
        if whole_results:
            hanzi = whole_results[0]['漢字']
            hanzi = re.sub(r'【.*?】', '', hanzi)
            if show_details:
                return f"{hanzi}\n(完整查詢: {whole_results[0]['羅馬字']})"
            return hanzi

        # 分割句子為詞彙（以空格分隔）
        words = tailo_sentence.split()

        translated_parts = []
        unknown_words = []
        details = []

        for word in words:
            # 跳過空字串
            if not word or word.strip() == '':
                continue

            # 查詢字典
            results = self.lookup(word)

            if results:
                # 取第一個結果的漢字
                # 移除 【】中的內容（如【替】）
                hanzi = results[0]['漢字']
                hanzi = re.sub(r'【.*?】', '', hanzi)
                translated_parts.append(hanzi)
                if show_details:
                    details.append(f"{word} -> {hanzi} ({results[0]['羅馬字']})")
            else:
                # 無法翻譯的詞彙保留原文
                translated_parts.append(f"[{word}]")
                unknown_words.append(word)
                if show_details:
                    details.append(f"{word} -> [未找到]")

        result = ''.join(translated_parts)

        # 如果有無法翻譯的詞彙，附加說明
        if unknown_words:
            result += f"\n(無法翻譯: {', '.join(unknown_words)})"

        if show_details and details:
            result += f"\n\n詳細查詢:\n" + "\n".join(details)

        return result

    def fuzzy_search(self, tailo_text: str, max_results: int = 10) -> List[Dict]:
        """
        模糊搜尋台羅文字

        參數:
            tailo_text: 台羅文字片段
            max_results: 最多返回的結果數量

        返回:
            符合的結果列表
        """
        normalized_input = self._normalize_tailo(tailo_text)
        results = []

        for idx, row in self.df.iterrows():
            roma_text = str(row['羅馬字']).lower()

            # 檢查是否包含搜尋文字
            if normalized_input in roma_text:
                results.append({
                    '漢字': row['漢字'],
                    '羅馬字': row['羅馬字'],
                    '分類': row['分類'],
                    '詞目類型': row['詞目類型']
                })

                if len(results) >= max_results:
                    break

        return results


def main():
    """測試用主程式"""
    import sys

    # 建立字典實例
    dictionary = TailoDictionary()

    if len(sys.argv) < 2:
        # 互動模式
        print("=== 台羅字典查詢系統 ===")
        print("指令:")
        print("  lookup <台羅文字>   - 精確查詢")
        print("  translate <台羅句子> - 翻譯整句")
        print("  search <台羅片段>    - 模糊搜尋")
        print("  quit                - 離開")
        print()

        while True:
            try:
                user_input = input("> ").strip()

                if not user_input:
                    continue

                if user_input.lower() == 'quit':
                    break

                parts = user_input.split(maxsplit=1)
                if len(parts) < 2:
                    print("請輸入指令和查詢文字")
                    continue

                command, query = parts

                if command == 'lookup':
                    results = dictionary.lookup(query)
                    if results:
                        print(f"\n找到 {len(results)} 筆結果:")
                        for i, r in enumerate(results, 1):
                            print(f"{i}. {r['漢字']} ({r['羅馬字']}) - {r['分類']}")
                    else:
                        print("查無此詞彙")

                elif command == 'translate':
                    result = dictionary.translate_sentence(query)
                    print(f"\n翻譯結果:\n{result}")

                elif command == 'search':
                    results = dictionary.fuzzy_search(query)
                    if results:
                        print(f"\n找到 {len(results)} 筆結果:")
                        for i, r in enumerate(results, 1):
                            print(f"{i}. {r['漢字']} ({r['羅馬字']}) - {r['分類']}")
                    else:
                        print("查無相關詞彙")

                else:
                    print(f"未知指令: {command}")

                print()

            except KeyboardInterrupt:
                print("\n再見！")
                break
            except Exception as e:
                print(f"錯誤: {e}")

    else:
        # 命令列模式
        tailo_text = sys.argv[1]
        print(f"查詢: {tailo_text}")
        print()

        results = dictionary.lookup(tailo_text)
        if results:
            print(f"找到 {len(results)} 筆結果:")
            for i, r in enumerate(results, 1):
                print(f"{i}. {r['漢字']} ({r['羅馬字']}) - {r['分類']}")
        else:
            print("查無此詞彙")


if __name__ == "__main__":
    main()
