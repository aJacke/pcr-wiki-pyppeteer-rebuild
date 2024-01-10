import pyppeteer
from pyppeteer import launch
from zhconv import convert
import asyncio
from data import *
import _pcr_data

UnavailableChara = {
    1000,   # 未知角色
    1067,   # 穗希
    1069,   # 霸瞳
    1072,   # 可萝爹
    1073,   # 拉基拉基
    1102,   # 泳装大眼
    1183,   # 初音(初音&栞)
    1184,   # 栞(初音&栞)
    1204,   # 美美(小小甜心)
    1205,   # 禊(小小甜心) 
    1206,   # 镜华(小小甜心)
    1217,   # 秋乃(秋乃&咲恋)
    1218,   # 咲恋(秋乃&咲恋)
    1908,
    4031,
    9000,
    9401,
}

# 改这里控制爬虫范围
head = 1223
end = 1299

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

async def chara_data(page, idx, name):
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
    return name

async def main():
    browser = await launch(devtools=True, args=['--disable-popup-blocking'])
    page = await browser.newPage()
    for idx, names in _pcr_data.CHARA_NAME.items():
        if idx >= head   and idx <= end and idx not in UnavailableChara:# 批量更新，自行替换为更新范围
        # if idx == 1156 and idx not in UnavailableChara:# 单条更新，此处数字更改为想要爬取的角色id
            name_zh = names[0].replace('(','（').replace(')','）')
            name = convert(f'{name_zh}', 'zh-hant').replace('憐','怜')
            # 特殊：怜（萬聖節）
            name = tw_name_replace(name)
            
            url = f'https://pcredivewiki.tw/Character/Detail/{name}'
            await page.goto(url, {'waitUntil': 'domcontentloaded'})
            await asyncio.sleep(20)

            title = await page.title()
            if "undefined" in title:
                url = f'https://pcredivewiki.tw/Character/Detail/{name_zh}'
                await page.goto(url, {'waitUntil': 'domcontentloaded'})
                await asyncio.sleep(20)
                title = page.title()
                if "undefined" in title:
                    name_jp = names[1].replace('(','（').replace(')','）')
                    url = f'https://pcredivewiki.tw/Character/Detail/{name_jp}'
                    await page.goto(url, {'waitUntil': 'domcontentloaded'})
                    await asyncio.sleep(20)
                    print(page.title())

            await chara_data(page, idx, name)


asyncio.get_event_loop().run_until_complete(main())
