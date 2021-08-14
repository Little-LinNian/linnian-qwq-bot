from pathlib import Path
from avilla.event import message
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
import random
import time
from avilla.execution.message import MessageSend
from avilla.message.chain import MessageChain
from avilla.relationship import Relationship
from avilla.builtins.profile import MemberProfile, GroupProfile
from avilla.builtins.elements import PlainText, Notice
from avilla.builtins.elements import Image
from avilla.event.message import MessageEvent
from lib.bank import Bank
import ujson
import lib.config as ucfg
import aiohttp
import aiofiles
from lib import cos
ABLE_USE_LIST = []
USERS_CONFIG = {}
saya = Saya.current()
channel = Channel.current()

@channel.use(ListenerSchema(listening_events= [MessageEvent]))
async def handle_message(event: MessageEvent, rs: Relationship[MemberProfile, GroupProfile]):
    global ABLE_USE_LIST
    global USERS_CONFIG
    if event.message.as_display().startswith("#i2lm add"):
        admin = await ucfg.get_config()
        if not rs.ctx.id ==  str(admin["ADMIN"][0]):
            await rs.exec(MessageSend([PlainText("你无权进行此操作 uwu")]))
            return
        if event.message.has(Notice):
            qid = event.message.get_first(Notice).target
            name = event.message.get_first(PlainText).text.split(" ")[2]
        else:
            qid = event.message.as_display().split(" ")[2]
            name = event.message.as_display().split(" ")[3]
        ABLE_USE_LIST.append(qid)
        USERS_CONFIG[qid] = name
        await rs.exec(MessageSend(MessageChain.create([PlainText(f"{name}已经被添加到使用名单中 uwu")])))
        async with aiofiles.open("./data/i2l.json", 'w') as f:
            await f.write(ujson.dumps({"enable_list":ABLE_USE_LIST, "user_config":USERS_CONFIG}))
       
    elif  event.message.as_display().startswith("#i2l"):
        print("ACTIVE")
        async with aiofiles.open("./data/i2l.json", 'r') as f:
            data:dict = ujson.loads(await f.read())

        ABLE_USE_LIST = data["enable_list"]
        USERS_CONFIG = data["user_config"]
        if rs.ctx.id not in ABLE_USE_LIST:
            await rs.exec(MessageSend(MessageChain.create([PlainText("你还没有被添加到使用名单中 uwu")])))
            return
        else:
            user_info = USERS_CONFIG[rs.ctx.id]
            if not event.message.has(Image):
                await rs.exec(MessageSend(MessageChain.create([PlainText("你好像什么图片都没发送 awa")])))
            else:
                image = event.message.get_first(Image).provider.url
                async with aiohttp.request('GET', image) as resp:
                    image_data = await resp.read()
                    image_path = Path("./data/img2link/img/{}.jpg".format(time.time()))
                    async with aiofiles.open(str(image_path), 'wb') as f:
                        await f.write(image_data)
                    await rs.exec(MessageSend(MessageChain.create([PlainText("你的图片已经收到啦，请等待图片转换为链接 awa")])))
                    resp = await cos.upload_file(image_path, user_info)
                    await rs.exec(MessageSend(MessageChain.create([PlainText(f"你的图片已经转换为链接，请点击{resp}查看图片 awa")])))

    else:
        return