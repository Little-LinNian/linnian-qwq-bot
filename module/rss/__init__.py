from pathlib import Path
import aiohttp
import re
import os
from avilla.core.builtins.profile import GroupProfile, MemberProfile
from avilla.core.provider import RawProvider
import loguru
import yaml
import asyncio
from lib import rss_parsers
from avilla.core.builtins.elements import Image, Text
from avilla.core.event.message import MessageEvent
from avilla.core.relationship import Relationship
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from avilla.core.message.chain import MessageChain
from avilla.core.exceptions import AccountMuted
from lib import img2text
from avilla.core.execution.message import MessageSend




saya = Saya.current()
channel = Channel.current()

rss_config = yaml.load(Path("./configs/rss.yml").read_text(),yaml.SafeLoader)
@channel.use(ListenerSchema(
    listening_events=[MessageEvent]
    )
)
async def network_compiler(
        event: MessageEvent,
        rs: Relationship
):
    if event.message.as_display().startswith("#lofter "):
        msg = event.message.as_display().replace("#lofter ", "")
        cmd = msg.split(" ")
        async def parse(id):
            try:
                resp = await rss_parsers.lofter_parser(f"https://rsshub.rainlong.cn/lofter/user/{id}")
                await rs.exec(MessageSend(MessageChain.create([Image(RawProvider( resp))])))
            except:
                await rs.exec(MessageSend(MessageChain.create([Text("貌似在Lofter没有这个id")])))

        if cmd[0] == "解析":
            loguru.logger.info(f"{rs.ctx.id} 解析 {cmd[1]}")
            id = cmd[1]
            await parse(id)
