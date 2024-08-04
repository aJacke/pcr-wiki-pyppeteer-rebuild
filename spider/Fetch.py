import pyppeteer
import asyncio
from data import *

async def extract_skill_icons_text(page, section_heading):
    result = []  # 创建一个空列表，用于存储提取的文本
    
    # 使用XPath来定位包含指定标题文本的元素
    heading_element = await page.xpath(f'//h4[contains(text(), "{section_heading}")]')

    if heading_element:
        # 找到包含指定标题文本的元素后，获取其父元素
        parent_element = await heading_element[0].getProperty('parentNode')
        
        if parent_element:
            # 在父元素下查找包含图片名称的所有img元素
            image_elements = await parent_element.xpath('.//img[starts-with(@src, "/static/images/skill/icon_skill_")]')
            
            if image_elements:
                # 提取每个图片名称中的文本，并添加到列表中
                for img_element in image_elements:
                    src_attribute = await img_element.getProperty('src')
                    image_src = await src_attribute.jsonValue()
                    text = image_src.split('icon_skill_')[1].split('.png')[0]
                    result.append(text)  # 添加到列表中
            else:
                print("No skill icons found")
        else:
            print(f"Parent element not found for '{section_heading}'")
    else:
        print(f"Element with '{section_heading}' not found")
    
    return result  # 返回存储的结果列表

async def get_chara_data(page, text, name, key):
    element = await page.xpath(f'//th[text()="{text}"]/..')
    if key == 'introduce':
        element = await page.xpath('//h3[text()="簡介"]/..')
        introduce = await page.evaluate('(element) => element.innerText', element[0])
        introduce = introduce.split('\n')[1]
        return introduce
    if len(element) == 0:
        return 0
    if key == 'infoelem':
        infoelem = await element[0].xpath('td/span')
        infoelem = await page.evaluate('(element) => element.getAttribute("class")', infoelem[0])
        infoelem = infoelem.split('mx-auto icon icon-ele ')[1]
        if infoelem == 't1':
            infoelem = "水"
        elif infoelem == 't2':
            infoelem = "火"
        elif infoelem == 't3':
            infoelem = "风"
        elif infoelem == 't4':
            infoelem = "光"
        elif infoelem == 't5':
            infoelem = "暗"
        else:
            infoelem = "未知属性"
        return infoelem
    keylist = [
        'guild',
        'birthday',
        'age',
        'height',
        'weight',
        'blood_type',
        'race',
        'hobby',
        'cv'
    ]
    if key in keylist:
        elem = await element[0].xpath('td')
        elem = await page.evaluate('(element) => element.innerText', elem[0])
        return elem

async def get_skill_data(page, text, name, key):
    element = await page.xpath(f'//div[text()="{text}"]/../..')
    if len(element) == 0: # 判断是否有技能信息
        return 0

    if key == 'img':
        img_element = await element[0].xpath('..//img[starts-with(@src, "/static/images/skill/icon_skill_")]')
        src_attribute = await img_element[0].getProperty('src')
        image_src = await src_attribute.jsonValue()
        img = image_src.split('icon_skill_')[1].split('.png')[0]
        return img

    elif key == 'description':
        description_element = await element[0].xpath('./div[starts-with(@class,"skill-de")]')
        skill_name = await description_element[0].xpath('./h3')
        name = await page.evaluate('(element) => element.innerText', skill_name[0])
        description = await page.evaluate('(element) => element.innerText', description_element[0])
        return description
    
    elif key == 'effect':
        effects = []
        effect_elements = await element[0].xpath('..//div[starts-with(@class,"skill-ef")]/div[starts-with(@class,"mb-2") and count(div) > 0]')
        for effect_element in effect_elements:
            skill_effect = await effect_element.xpath('./div')
            effect = await page.evaluate('(element) => element.innerText', skill_effect[0])
            effects.append(effect)
        return effects

async def get_kizuna_data(page):
    elements = await page.xpath('//table[starts-with(@class,"chara-table")]/tbody') # /td/div/div
    namelist = []
    kzn = []
    for element in elements:
        name = await element.xpath('tr/th')
        name = await page.evaluate('(element) => element.innerText', name[0])
        if name in namelist:
            continue
        namelist.append(name)
        kzn_lists = await element.xpath('tr/td/..')
        for kzn_list in kzn_lists:
            episode = await kzn_list.xpath('th')
            effect = await kzn_list.xpath('td')
            episode = await page.evaluate('(element) => element.innerText', episode[0])
            episode = episode.split('\t')[0]
            effect = await page.evaluate('(element) => element.innerText', effect[0])
            effect = effect.split('\n')
            kzndata = []
            kzndata.append(name)
            kzndata.append(episode)
            kzndata.append(effect)
            kzn.append(kzndata)
    return kzn

async def get_uniquei_data(page, text): # 给专武2留个口子(bushi)
    element = await page.xpath(f'//h3[text()="{text}"]/../div')
    name = await element[0].xpath('h2')
    name = await page.evaluate('(element) => element.innerText', name[0])
    img = await element[0].xpath('div//img')
    src_attribute = await img[0].getProperty('src')
    img_src = await src_attribute.jsonValue()
    num = img_src.split('/static/images/equipment/icon_equipment_')[1].split('.png')[0]
    description = await element[0].xpath('.//p')
    description = await page.evaluate('(element) => element.innerText', description[0])
    list = [num, name, description]
    return list

async def get_props_data(page, text):
    element = await page.xpath(f'//h3[text()="{text}"]/../div')
    propertys = await element[0].xpath('div//span[starts-with(@class, "title")]')
    props_list = []
    for property in propertys:
        text = await property.xpath('../span')
        text = await page.evaluate('(element) => element.innerText', text[1])
        property = await page.evaluate('(element) => element.innerText', property)
        base_value = text.split('(')[0].split(' ')[0]
        max_value = text.split('(')[1].split(')')[0]
        propList = []
        propList.append(property)
        propList.append(base_value)
        propList.append(max_value)
        props_list.append(propList)
    return props_list


# 之后可能会慢慢做的更精简一点 比如别调用多次之类的 现在先保证能用
async def chara_data(page, idx, name):
    element = await get_chara_data(page, "屬性", name, 'infoelem')
    guild = await get_chara_data(page, "公會", name, 'guild')
    birthday = await get_chara_data(page, "生日", name, 'birthday')
    age = await get_chara_data(page, "年齡", name, 'age')
    height = await get_chara_data(page, "身高", name, 'height')
    weight = await get_chara_data(page, "體重", name, 'weight')
    blood_type = await get_chara_data(page, "血型", name, 'blood_type')
    race = await get_chara_data(page, "種族", name, 'race')
    hobby = await get_chara_data(page, "喜好", name, 'hobby')
    cv = await get_chara_data(page, "聲優", name, 'cv')
    introduce = await get_chara_data(page, "簡介", name, 'introduce')
    start = await extract_skill_icons_text(page, '起手')
    loop = await extract_skill_icons_text(page, '循環')

    month, day = birthday.split(" / ")
    birthday = f"{month}月{day}日"

    Info.replace(
        id=idx,
        name = name,
        element = element,
        guild = guild,
        birthday = birthday,
        age = age,
        height = height,
        weight = weight,
        blood_type = blood_type,
        race = race,
        hobby = hobby,
        cv = cv,
        introduce = introduce,
        start = ','.join(start),
        loop = ','.join(loop),
    ).execute()

async def skill_data(page, idx, name):
    types = ['必殺技', '必殺技+', '技能1', '專武強化技能1', '技能2', '專武強化技能2', 'EX技能', 'EX技能+']
    # types = ['必殺技', '必殺技+', '技能1', '專武強化技能1', '技能2', 'EX技能', 'EX技能+']
    for type in types:
        num = await get_skill_data(page, type, name, 'img')
        if num == 0:
            continue
        description = await get_skill_data(page, type, name, 'description')
        name = description.strip().split('\n')[1]
        description = description.strip().split('\n')[2]
        effect = await get_skill_data(page, type, name, 'effect')

        Skill.replace(
            id = idx,
            name = name,
            type = type,
            description = description,
            num = num,
            effect = effect,
        ).execute()

async def kizuna_data(page, idx, name):
    kzndata = await get_kizuna_data(page)
    i = 0
    Kizuna.delete().where(Kizuna.id == idx).execute()
    while (i < len(kzndata)):
        name = kzndata[i][0]
        episode = kzndata[i][1]
        effect = kzndata[i][2]
        
        Kizuna.replace(
            id = idx,   
            name = name,
            episode = episode,
            effect = effect,
        ).execute()

        i += 1

async def uniquei_data(page, idx, name):
    Nofind = []
    Uniquei.delete().where(Uniquei.id == idx).execute()
    for uni in ['專武 1', '專武 2']:
        try:
            uniquei_list = await get_uniquei_data(page, uni)
        except:
            Nofind.append(uni)
            continue
        name = uniquei_list[1]
        num = uniquei_list[0]
        description = uniquei_list[2]
        # 清除/n
        description = description.replace('\\', '')
        Uniquei.replace(
            id = idx,   
            name = name,
            num = num,
            description = description,
        ).execute()
        await props_data(page, idx, uni, num)
    return Nofind

async def props_data(page, idx, uni, num):
    props_list = await get_props_data(page, uni)
    i = 0
    Props.delete().where(Props.id == idx).execute()
    while (i < len(props_list)):
        property = props_list[i][0]
        base_value = props_list[i][1]
        max_value = props_list[i][2]
        Props.replace(
            id = num,
            property = property,
            base_value = base_value,
            max_value = max_value,
        ).execute()
        i += 1