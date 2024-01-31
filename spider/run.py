import pyppeteer
from pyppeteer import launch
from zhconv import convert
import asyncio
from data import *
from Fetch import *
from twNameReplace import *
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
head = 1275
end = 1300
# 让我看看爬虫过程(True/False)
headless_model = False

async def main():
    browser = await launch(headless = headless_model, args=['--disable-popup-blocking'])
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
                title = await page.title()
                if "undefined" in title:
                    name_jp = names[1].replace('(','（').replace(')','）')
                    url = f'https://pcredivewiki.tw/Character/Detail/{name_jp}'
                    await page.goto(url, {'waitUntil': 'domcontentloaded'})
                    await asyncio.sleep(20)
                    ''' 还不确定这个东西能不能用 感觉没起作用
                    if "undefined" in title:
                        print("没找到" + name + "的数据。若有需要，请提issue")
                    '''
                    await chara_data(page, idx, name)
                    await skill_data(page, idx, name)


asyncio.get_event_loop().run_until_complete(main())
