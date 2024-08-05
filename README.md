# pcr-wiki插件

本插件需配合[Hoshino(v2)](https://github.com/Ice-Cirno/HoshinoBot)使用

数据搬运于[蘭德索爾圖書館](https://pcredivewiki.tw/)，图片资源来源[干炸里脊资源站](https://redive.estertion.win/)

fork于[pcr-wiki插件](https://github.com/pcrbot/pcr-wiki)

## 功能

- **[@bot简介ue] 角色简介**：查询角色简介
- **[@bot技能ue] 角色技能**：查询角色技能
- **[@bot专武ue] 角色专武**：查询角色专武
- **[@bot羁绊ue] 角色羁绊**：查询角色羁绊
- **启用wiki**：启用wiki
- **禁用wiki**：禁用wiki
- <s>**更新wiki**：更新wiki数据   这个怎么说呢，我还不知道怎么实现</s>

## 部署

1. 将本项目的`wiki`文件夹复制到`hoshino/modules/priconne`下

2. 安装`requirements.txt`

3. 将本项目的`skill`与`equipment`文件夹复制到`res/img/priconne`文件夹下面

   > 实际上，只需要新建`skill`与`equipment`文件夹并把`skill`下的`icon_skill_ap01.png`、`icon_skill_ap02.png`、`icon_skill_attack.png`、`icon_skill_tack.png`四个图片复制过去就好，其他没有的图片使用时会自动下载

4. 重启Hoshino

   > 注意：**不要**在hoshino的配置文件添加模块。
   >
   > 注意：**不要**把`spider`文件夹及该文件夹下的文件任何文件放到`hoshino`下

至此，你可以开始使用插件了。

插件的数据源自文件夹下的`data.db`，`data.db`会不定时更新(Releases里手动下载或使用更新命令更新，一般在图书馆更新了新角色，新专武后我会更新)，如果你想要自己手动更新，请看下一小节

## 手动更新数据(PS:学艺不精，望佬轻喷)

> 强烈建议在windows机器上更新数据，更为快速方便。`spider`文件夹仅作更新数据使用，**不要**把这个文件夹混入`hoshino`的任何目录，它是独立的

#### windows

1. 打开`spider`文件夹，安装`requirements.txt`

2. 将你需要更新的`data.db`准备好

3. 打开`run.py`按照注释修改对应处（第32、33行），打开`data.py`按照注释修改第3行

4. 将你最新的`_pcr_data.py`复制到`spider`文件夹下替换（保证`spider/_pcr_data.py`里有你需要更新的id信息）<s>其实正常情况下，spider文件夹内自带了`_pcr_data.py`且会自动更新，不想复制也能`git pull`就是了</s>

5. 运行`run.py`

6. 若无报错，则更新成功，得到最新的`data.db`，替换掉你`hoshino/modules/priconne/wiki`下的同名件

#### Linux

没做测试，有测试过的大佬可以pr

可以参考原插件教程

