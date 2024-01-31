def tw_name_replace(name):
    if "時間旅行" in name:
        name = name.replace("時間旅行", "時空旅行")
    if "作業服" in name:
        name = name.replace("作業服", "工作服") # 哪个小可爱给他翻成作业服的，我给你上个buff
    if "貪喫佩可" in name:
        name = name.replace("喫", "吃") # 逆天转换
    if "舞臺" in name:
        name = name.replace("臺", "台")
    if "斑比" in name:
        name = name.replace("斑", "班")
    if "野性" in name:
        name = name.replace("野性", "狂野")
    if "裏" in name:
        name = name.replace("裏", "里") # 我是真服了，排除翻译，这繁简转换是真的离谱
    if "咖啡館" in name:
        name = name.replace("館", "廳") # 应该不会再有翻译问题了吧，后面基本上都是我提交的_pcr_data.py了
    if "姬塔" in name:
        name = name.replace("姬", "吉") # 名字的话当我没说
    if "鍊金術士" in name:
        name = name.replace("士", "師") # 这不能怪我，他网页上的名字和资讯里的不一致
    # 不是，兰得索尔图书馆这网页命名怎么回事，怎么和资讯名字对不上了开始
    if "（墮天使）" in name:
        name = name.replace("墮天使","墮落")
    if "古蕾雅" in name:
        name = name.replace("雅", "婭")
    if "&古" in name:
        name = name.replace("&", "＆") # 这还真是我更出来的好事，麻了，但是图书馆也没统一用哪个
    return name