import json

# 定义品牌集合
BRANDS = [
    'Andrew Gn', 'Armani Privé', 'Belstaff', 'Betsey Johnson', 
    'Blumarine', 'Celine', 'Chanel', 'Chloé', 'Dior', 
    'Dolce & Gabbana', 'Elie Saab', 'Elisabetta Franchi', 
    'Emanuel Ungaro', 'Georges Hobeika', 'Isabel Marant', 
    'Lolita Lempicka', 'Luisa Beccaria', 'Maison Wester', 
    'Max Mara', 'Olympia Le-Tan', 'Oscar de la Renta', 
    'Rachel Lai', 'Ralph Lauren', 'Ralph & Russo', 
    'Red Valentino', 'Rochas', 'Sretsis', 'The Atelier', 
    'Tory Burch', 'Valentino', 'Yves Saint Laurent', 'Zuhair Murad'
]

# 将品牌列表转为 set，提高查找效率
BRAND_SET = set(BRANDS)

def process_jsonl(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as fin, \
         open(output_file, 'w', encoding='utf-8') as fout:
        
        for line in fin:
            line = line.strip()
            if not line:
                continue
            
            data = json.loads(line)
            tags = data.get('tags', [])

            # 1. 提取 category (tags 中的第一个值)
            category = tags.pop(0) if tags else ""

            # 2. 提取 image_type (tags 中的第二个值，此时已被移出第一个，所以继续取 0 索引)
            image_type = tags.pop(0) if tags else ""

            # 3. 提取 brand (遍历 tags，比对是否存在于品牌集合中)
            brand = ""
            for tag in list(tags):
                if tag in BRAND_SET:
                    brand = tag
                    tags.remove(tag)
                    break  # 假设每行最多匹配到一个品牌

            # 4. 重新构建字段顺序（保证三个新字段紧跟在 image_url 后面）
            new_data = {}
            for key, value in data.items():
                new_data[key] = value
                if key == 'image_url':
                    new_data['category'] = category
                    new_data['image_type'] = image_type
                    new_data['brand'] = brand

            # 写入新的 JSONL 文件
            fout.write(json.dumps(new_data, ensure_ascii=False) + '\n')

if __name__ == '__main__':
    # 替换为你的实际文件名
    input_filename = 'scripts/clothing/clothing.jsonl'
    output_filename = 'scripts/clothing/clothing_processed.jsonl'
    
    process_jsonl(input_filename, output_filename)
    print("处理完成！")