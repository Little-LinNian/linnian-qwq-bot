from datetime import datetime
from io import BytesIO
from os import path, wait
from pathlib import Path
from PIL import Image as im
from avilla.builtins.profile import GroupProfile, MemberProfile
from .rua_data.data_source import generate_gif
import aiohttp
import loguru
import os
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from lib import limiter
from avilla.execution.message import MessageSend
from avilla.message.chain import MessageChain
from avilla.relationship import Relationship
from avilla.builtins.elements import Image, PlainText, Notice
from avilla.event.message import MessageEvent

saya = Saya.current()
channel = Channel.current()
import asyncio

wait_list = {}
data_dir = os.path.join(path.dirname(__file__), "rua_data/data")


async def ruaer(id):
    url = f"http://q1.qlogo.cn/g?b=qq&nk={id}&s=160"
    async with aiohttp.request("get", url) as resp:
        resp_cont = await resp.read()
    avatar = im.open(BytesIO(resp_cont))
    output = generate_gif(data_dir, avatar)
    return output


@channel.use(ListenerSchema(listening_events=[MessageEvent]))
async def rua(event: MessageEvent, rs: Relationship[MemberProfile,GroupProfile]):
    if event.message.has(Notice) and event.message.get_first(PlainText).text == "搓":

        await limiter.limit("rua", rs, 5)
        qid = event.message.get(Notice)[0].target
        url = await ruaer(qid)
        await rs.exec(
            MessageSend(MessageChain.create([Image.fromLocalFile(Path(url))]))
        )
    else:
        pass
