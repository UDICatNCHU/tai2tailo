#!/usr/bin/env python3
"""
台羅斷詞查詢工具
用於提供給 LLM 進行翻譯的字詞候選
"""

from tailo_dictionary import TailoDictionary
import json
import sys

def main():
    # 檢查命令列參數
    if len(sys.argv) < 2:
        print("使用方式: python3 example_segment_lookup.py <台羅句子> [選項]")
        print()
        print("範例:")
        print("  python3 example_segment_lookup.py \"guá ài lí\"")
        print("  python3 example_segment_lookup.py \"Guá beh khì i-sing-kuán\" --json")
        print("  python3 example_segment_lookup.py \"lí hó\" --max-candidates 3")
        print()
        print("選項:")
        print("  --json              只輸出 JSON 格式")
        print("  --max-candidates N  每個詞最多返回 N 個候選 (預設: 5)")
        print("  --help              顯示此說明")
        sys.exit(1)

    # 解析參數
    sentence = sys.argv[1]
    json_only = "--json" in sys.argv
    max_candidates = 5

    # 解析 max-candidates 參數
    for i, arg in enumerate(sys.argv):
        if arg == "--max-candidates" and i + 1 < len(sys.argv):
            try:
                max_candidates = int(sys.argv[i + 1])
            except ValueError:
                print(f"錯誤: --max-candidates 的值必須是數字")
                sys.exit(1)

    # 初始化字典
    dictionary = TailoDictionary("kautian.ods")

    # 斷詞並查詢每個詞的候選翻譯
    results = dictionary.segment_and_lookup(sentence, max_candidates=max_candidates)

    # 簡化格式
    simplified = []
    for word_result in results:
        options = []
        for c in word_result['candidates']:
            # 處理 NaN 值
            category = c['分類'] if c['分類'] == c['分類'] else None
            options.append({
                "chinese": c['漢字_清理'],
                "romanization": c['羅馬字'],
                "category": category,
                "type": c['詞目類型']
            })

        simplified.append({
            "tailo": word_result['tailo'],
            "found": word_result['found'],
            "options": options
        })

    # 只輸出 JSON 模式
    if json_only:
        print(json.dumps(simplified, ensure_ascii=False, indent=2))
        return

    # 完整輸出模式
    print(f"輸入台羅句子: {sentence}\n")

    print("=" * 70)
    print("每個詞的候選翻譯:")
    print("=" * 70)

    for word_result in results:
        print(f"\n台羅: {word_result['tailo']}")
        print(f"找到候選: {'✓' if word_result['found'] else '✗'}")

        if word_result['candidates']:
            print("候選翻譯:")
            for i, candidate in enumerate(word_result['candidates'], 1):
                category = candidate['分類'] if candidate['分類'] == candidate['分類'] else '(無分類)'
                print(f"  {i}. {candidate['漢字_清理']:10} "
                      f"(羅馬字: {candidate['羅馬字']:25}) "
                      f"分類: {category}")
        else:
            print("  ⚠ 無候選翻譯")

    # 輸出 JSON 格式
    print("\n\n" + "=" * 70)
    print("JSON 格式輸出（給 LLM 使用）:")
    print("=" * 70)
    print(json.dumps(simplified, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
