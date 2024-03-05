import pyppeteer
import asyncio
from data import *

async def find_td_text_by_th_text(page, text_to_find):
    # 使用JavaScript来查找包含特定文本的<th>元素
    th_element = await page.evaluateHandle('''(textToFind) => {
        const thElements = document.querySelectorAll('th');
        for (const th of thElements) {
            if (th.textContent.trim() === textToFind) {
                return th;
            }
        }
        return null;
    }''', text_to_find)

    if th_element:
        # 找到包含特定标题的<th>元素，然后找到其父级<tr>元素
        tr_element = await page.evaluateHandle('(th) => th.closest("tr")', th_element)
        
        if tr_element:
            # 找到<tr>元素后，可以继续查找包含内容的<td>元素
            td_element = await page.evaluateHandle('(tr) => tr.querySelector("td").textContent', tr_element)

            if td_element:
                # 如果找到<td>元素，获取其文本内容
                td_text = await td_element.jsonValue()
                return td_text
    return None

async def extract_text_after_heading(page, heading_text):
    # 使用XPath来定位包含指定标题文本的元素
    heading_element = await page.xpath(f'//h3[contains(text(), "{heading_text}")]')

    if heading_element:
        # 如果找到包含指定标题文本的元素，使用page.evaluate来获取文本内容
        extracted_text = await page.evaluate('(element) => element.nextSibling.textContent.trim()', heading_element[0])

        if extracted_text:
            return extracted_text
    return None

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

async def get_chara_data(page, text, name, key): # 有剩下的有空在做吧
    element = await page.xpath(f'//th[text()="{text}"]/..')
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


async def chara_data(page, idx, name):
    element = await get_chara_data(page, "屬性", name, 'infoelem')
    guild = await find_td_text_by_th_text(page, "公會")
    birthday = await find_td_text_by_th_text(page, "生日")
    age = await find_td_text_by_th_text(page, "年齡")
    height = await find_td_text_by_th_text(page, "身高")
    weight = await find_td_text_by_th_text(page, "體重")
    blood_type = await find_td_text_by_th_text(page, "血型")
    race = await find_td_text_by_th_text(page, "種族")
    hobby = await find_td_text_by_th_text(page, "喜好")
    cv = await find_td_text_by_th_text(page, "聲優")
    introduce = await extract_text_after_heading(page, "簡介")
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
    # types = ['必殺技', '必殺技+', '技能1', '專武強化技能1', '技能2', '專武強化技能2', 'EX技能', 'EX技能+'] 图书馆好像还没专2技能的数据，先放着
    types = ['必殺技', '必殺技+', '技能1', '專武強化技能1', '技能2', 'EX技能', 'EX技能+']
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