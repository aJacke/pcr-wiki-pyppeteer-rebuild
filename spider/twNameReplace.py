tw_name_list = {
    "時間旅行": "時空旅行",  
    "作業服": "工作服",  
    "貪喫佩可": "貪吃佩可",  
    "舞臺": "舞台",  
    "斑比": "班比",  
    "野性": "狂野",  
    "裏": "里",  
    "咖啡館": "咖啡廳",  
    "姬塔": "吉塔",  
    "鍊金術士": "鍊金術師",  
    "墮天使": "墮落",  
    "古蕾雅": "古蕾婭",  
    "&": "＆",  
    "莎拉沙利亞": "薩拉薩利亞",  
    "真那": "霸瞳皇帝",
    "厄里斯": "厄莉絲",
    "星辰": "星素"
}


def tw_name_replace(name):
    for old, new in tw_name_list.items():  
        if old in name:  
            name = name.replace(old, new) 
    
    # 单独处理咲哈哈
    if "秋乃＆咲戀" in name:
        name = name.replace("＆", "&")

    return name
