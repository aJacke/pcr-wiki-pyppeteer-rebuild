import os
import peewee as pw
import requests
import functools
import hashlib
from PIL import Image
from io import BytesIO
from zhconv import convert
from hoshino import R, log
from hoshino.typing import MessageSegment
from hoshino.util import pic2b64

logger = log.new_logger('wiki')

UNKNOWN = 1000

def get_file_md5():
    myhash = hashlib.md5()
    f = open(os.path.join(os.path.dirname(__file__), 'data.db'), "rb")
    while True:
        b = f.read(8096)
        if not b:
            break
        myhash.update(b)
    f.close()
    return myhash.hexdigest()

def custom_sorted(x,y):
    # order = ['必殺技','必殺技+','技能1','專武強化技能1','技能2','EX技能','EX技能+','特殊必殺技','特殊技能1','特殊技能1+','特殊技能2','特殊技能3']
    order = ['必殺技', '必殺技+', '技能1', '專武強化技能1', '技能2', '專武強化技能2', 'EX技能', 'EX技能+','特殊技能1','特殊技能1+','特殊技能2','特殊技能3']
    if order.index(x['type']) < order.index(y['type']):
        return -1
    if order.index(x['type']) > order.index(y['type']):
        return 1
    return 0

def download_icon(num, types):
    url = f'https://redive.estertion.win/icon/{types}/{num}.webp'
    save_path = R.img(f'priconne/{types}/icon_{types}_{num}.png').path
    logger.info(f'Downloading {types} icon from {url}')
    try:
        rsp = requests.get(url, stream=True, timeout=5)
    except Exception as e:
        logger.error(f'Failed to download {url}. {type(e)}')
        logger.exception(e)
    if 200 == rsp.status_code:
        img = Image.open(BytesIO(rsp.content))
        img.save(save_path)
        logger.info(f'Saved to {save_path}')
    else:
        logger.error(f'Failed to download {url}. HTTP {rsp.status_code}')

def icon(num, types):
    res = R.img(f'priconne/{types}/icon_{types}_{num}.png')
    if not res.exist:
        download_icon(num, types)
        res = R.img(f'priconne/{types}/icon_{types}_{num}.png')
    if not res.exist:
        res = R.img(f'priconne/unit/icon_unit_{UNKNOWN}31.png')
    return res

def resize_icon(num,size=64,types='skill'):
    pic = icon(num,types).open().convert('RGBA').resize((size, size), Image.LANCZOS)
    return str(MessageSegment.image(pic2b64(pic)))

def get_icons(arr,size=64,types='skill'):
    num = len(arr)
    des = Image.new('RGBA', (num*size, size), (255, 255, 255, 255))
    for i, chara in enumerate(arr):
        pic = icon(chara,types).open().convert('RGBA').resize((size, size), Image.LANCZOS)
        des.paste(pic, (i * size, 0), pic)
    return str(MessageSegment.image(pic2b64(des)))

def get_info(id):
    query = Info.get(Info.id==id)
    msg = f'\n屬性: {query.element}\n公會: {query.guild}\n生日: {query.birthday}\n年齡: {query.age}\n身高: {query.height}\n體重: {query.weight}\n血型: {query.blood_type}\n種族: {query.race}\n喜好: {query.hobby}\nCV: {query.cv}\n簡介: {query.introduce}'
    return convert(msg, 'zh-hans')

def get_skill(id):
    loop = Info.get(Info.id==id)
    query = Skill.select().where(Skill.id==id)
    arr = []
    for i in query:
        skill = {}
        skill['name'] = i.name
        skill['type'] = i.type
        skill['description'] = i.description
        skill['num'] = i.num
        skill['effect'] = i.effect
        arr.append(skill)
    newlist = sorted(arr, key=functools.cmp_to_key(custom_sorted)) 
    msg = ''
    start = get_icons(loop.start.split(','))
    msg += f'\n起手：\n{start}\n'
    loop = get_icons(loop.loop.split(','))
    msg += f'循环：\n{loop}\n'
    msg += '技能：'
    for s in newlist:
        msg += '\n======================\n'
        msg += f'{s["type"]}:{s["name"]}\n'
        msg += f'{resize_icon(s["num"])}\n'
        msg += f'描述：\n{s["description"]}\n'
        effect = s["effect"].strip( "[']" )
        msg += '效果：\n'
        for e in effect.split("', '"):
            msg += f'{e}'
    return convert(msg, 'zh-hans')

def get_uniquei(id):
    query = Uniquei.get_or_none(Uniquei.id==id)
    if query:
        query = Uniquei.select().where(Uniquei.id==id)
        numlist = []
        namelist = []
        descriptionlist = []
        for record in query:
            numlist.append(record.num)
            namelist.append(record.name)
            descriptionlist.append(record.description)
        skill = Skill.get(Skill.id==id,Skill.type=='技能1')
        skill1 = Skill.get(Skill.id==id,Skill.type=='專武強化技能1')
        num1= numlist[0]
        name1 = namelist[0]
        e_icon1 = resize_icon(num1,types='equipment')
        prop1 = Props.select().where(Props.id==num1)
        description1 = descriptionlist[0]
        msg = ''
        msg += f'\n{name1}\n'
        msg += f'{e_icon1}\n'
        msg += f'{description1}'
        msg += '\n======================\n'
        for i in prop1:
            msg += f'{i.property}：{i.base_value}-{i.max_value}\n'
        msg += '======================\n'
        msg += f'{skill.type}:{skill.name}\n'
        msg += f'{resize_icon(skill.num)}\n'
        msg += f'描述：\n{skill.description}\n'
        effect = skill.effect.strip( "[']" )
        msg += '效果：\n'
        for e in effect.split("', '"):
            msg += f'{e}'
        msg += '\n======================\n'
        msg += f'{skill1.type}:{skill1.name}\n'
        msg += f'{resize_icon(skill1.num)}\n'
        msg += f'描述：\n{skill1.description}\n'
        effect1 = skill1.effect.strip( "[']" )
        msg += '效果：\n'
        for e in effect1.split("', '"):
            msg += f'{e}'
        try:
            num2 = numlist[1]
        except:
            return convert(msg, 'zh-hans')
        name2 = namelist[1]
        description2 = descriptionlist[1]
        e_icon2 = resize_icon(num2,types='equipment')
        prop2 = Props.select().where(Props.id==num2)
        skill2 = Skill.get(Skill.id==id,Skill.type=='技能2')
        skill3 = Skill.get(Skill.id==id,Skill.type=='專武強化技能2')
        msg += '\n======================'
        msg += f'\n{name2}\n'
        msg += f'{e_icon2}\n'
        msg += f'{description2}'
        msg += '\n======================\n'
        for i in prop2:
            msg += f'{i.property}：{i.base_value}-{i.max_value}\n'
        msg += '======================\n'
        msg += f'{skill2.type}:{skill2.name}\n'
        msg += f'{resize_icon(skill2.num)}\n'
        msg += f'描述：\n{skill2.description}\n'
        effect = skill2.effect.strip( "[']" )
        msg += '效果：\n'
        for e in effect.split("', '"):
            msg += f'{e}'
        msg += '\n======================\n'
        msg += f'{skill3.type}:{skill3.name}\n'
        msg += f'{resize_icon(skill3.num)}\n'
        msg += f'描述：\n{skill3.description}\n'
        effect2 = skill3.effect.strip( "[']" )
        msg += '效果：\n'
        for e in effect2.split("', '"):
            msg += f'{e}'
        return convert(msg, 'zh-hans')
    else:
        return '\n该角色暂时没有专武。'

def get_kizuna(id):
    query = Kizuna.select().where(Kizuna.id==id)
    arr = []
    for i in query:
        skill = {}
        skill['name'] = i.name
        skill['episode'] = i.episode
        skill['effect'] = i.effect
        arr.append(skill)
    newlist = sorted( arr ,key=lambda k: (len(k['name']), k['episode'][2]))
    msg = ''
    for i in newlist:
        msg += f'\n*{i["name"]}-{i["episode"]}:'
        for j in i["effect"].strip( "[']" ).split("', '"):
            msg += f' {j}'
    return convert(msg, 'zh-hans')

db = pw.SqliteDatabase(os.path.join(os.path.dirname(__file__), 'data.db'))

class Info(pw.Model):
    id = pw.IntegerField()
    name = pw.TextField()
    element = pw.TextField()
    guild = pw.TextField()
    birthday = pw.TextField()
    age = pw.TextField()
    height = pw.TextField()
    weight = pw.TextField()
    blood_type = pw.TextField()
    race = pw.TextField()
    hobby = pw.TextField()
    cv = pw.TextField()
    introduce = pw.TextField()
    start = pw.TextField()
    loop = pw.TextField()
    class Meta:
        database = db
        table_name = 'info'

class Skill(pw.Model):
    id = pw.IntegerField()
    name = pw.TextField()
    type = pw.TextField()
    description = pw.TextField()
    num = pw.TextField()
    effect = pw.TextField()
    class Meta:
        database = db
        table_name = 'skill'

class Kizuna(pw.Model):
    id = pw.IntegerField()
    name = pw.TextField()
    episode = pw.TextField()
    effect = pw.TextField()
    class Meta:
        database = db
        table_name = 'kizuna'

class Uniquei(pw.Model):
    id = pw.IntegerField()
    name = pw.TextField()
    num = pw.TextField()
    description = pw.TextField()
    class Meta:
        database = db
        table_name = 'uniquei'

class Props(pw.Model):
    id = pw.IntegerField()
    property = pw.TextField()
    base_value = pw.TextField()
    max_value = pw.TextField()
    class Meta:
        database = db
        table_name = 'props'