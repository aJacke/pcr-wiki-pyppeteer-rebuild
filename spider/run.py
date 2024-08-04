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
    1234,   # 纯(露营)
    1243,   # 安(安&古蕾雅)
    1244,   # 古蕾雅(安&古蕾雅)
    1281,   # 静流(静流&璃乃)
    1282,   # 璃乃(静流&璃乃)
    1701,   # 环奈
    1908,
    4031,
    9000,
    9401,
}

# 改这里控制爬虫范围
# 24/08/04 1299 惠理子(指挥官) 数据确实简介，暂未更新
head = 1800
end = 1900
# 等待时长 网络较慢时可以调高 但不能太低
waittime = 20
# 让我看看爬虫过程(True/False)
headless_model = False
# 最大重连次数
max_retries = 5
# 重试等待时间
retrytime = 5

# 设置一个连接网页的函数，用于重连
async def web_connect(page, url, idx):
    retries = 0
    while retries < max_retries:
        try:
            await page.goto(url, {'waitUntil': 'domcontentloaded'})
            break
        except Exception as e:
            print(f"页面加载失败: {e}, 正在重试")
            retries += 1
            await asyncio.sleep(retrytime)
    else:
        print(f"已到达最大重试次数，请检查网络链接并重试。失败编号{idx}")
        exit()
    return page

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
            page = await web_connect(page, url, idx)
            await asyncio.sleep(waittime)

            title = await page.title()
            if "undefined" in title:
                name_jp = names[1].replace('(','（').replace(')','）')
                if "&" in name_jp: # 专门写给日文&的，图书馆这&我是真的服气
                    name_jp = name_jp.replace("&", "＆")
                url = f'https://pcredivewiki.tw/Character/Detail/{name_jp}'
                page = await web_connect(page, url, idx)
                await asyncio.sleep(waittime)
                title = await page.title()
                if "undefined" in title:
                    url = f'https://pcredivewiki.tw/Character/Detail/{name_zh}'
                    page = await web_connect(page, url, idx)
                    await asyncio.sleep(waittime)
                    if "undefined" in title:
                        print(f'没找到{name}的数据。若有需要，请提issue')
                        continue
                    
            await chara_data(page, idx, name)
            await skill_data(page, idx, name)
            await kizuna_data(page, idx, name)
            Nofind = await uniquei_data(page, idx, name)
            if Nofind:
                print(f'{name_zh},该角色暂未找到{Nofind}数据。')
            # 下面这段代码为了方便查看更新进程
            # print (f'{name_zh}数据更新完毕')

asyncio.get_event_loop().run_until_complete(main())