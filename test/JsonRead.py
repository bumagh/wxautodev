import json

# 写入JSON文件
data = {
  "word_pairs": [
  ]
}

# 从JSON文件读取
with open('word_pairs.json', 'r', encoding='utf-8') as f:
    loaded_data = json.load(f)

# 使用词汇对列表
word_pairs = loaded_data['word_pairs']
print(f"共加载 {len(word_pairs)} 个词汇对")
for pair in word_pairs[:50]:  # 打印前5个示例
    print(f"{pair[0]} - {pair[1]}")