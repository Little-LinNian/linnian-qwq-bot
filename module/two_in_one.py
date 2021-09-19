from pathlib import Path
from avilla.core.event import message
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
import random
import base64
import time
from avilla.core.provider import RawProvider
from avilla.core.execution.message import MessageSend
from avilla.core.message.chain import MessageChain
from avilla.core.relationship import Relationship
from avilla.core.builtins.profile import MemberProfile, GroupProfile
from avilla.core.builtins.elements import Text, Notice
from avilla.core.builtins.elements import Image
from avilla.core.event.message import MessageEvent
from lib.bank import Bank
import ujson
import lib.config as ucfg
import aiohttp

saya = Saya.current()
channel = Channel.current()


@channel.use(ListenerSchema(listening_events=[MessageEvent]))
async def handle_message(
    event: MessageEvent, rs: Relationship
):
    if not event.message.as_display().startswith("#转基因"):
        return
    message = event.message
    if not message.has(Image) or len(message.get(Image)) != 2:
        await rs.exec(MessageSend(MessageChain.create([Text("要发两张图片哦 uwu")])))
        return
    image1 = message.get(Image)[0].provider.url
    image2 = message.get(Image)[1].provider.url
    config = await ucfg.get_config()
    data = {
        "api_key": config["facekey"],
        "api_secret": config["facesecret"],
        "template_url": image1,
        "merge_url": image2,
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api-cn.faceplusplus.com/imagepp/v1/mergeface", data=data
        ) as resp:
            resp_data = await resp.json()
            if "result" in resp_data:
                result = resp_data["result"]
                result_bytes = base64.b64decode(result)
                await rs.exec(
                    MessageSend(
                        MessageChain.create(
                            [Text("转基因成功 uwu"), Image(RawProvider(result_bytes))]
                        )
                    )
                )
            if "error_message" in resp_data:
                await rs.exec(
                    MessageSend(
                        MessageChain.create(
                            [
                                Text("转基因失败 qwq\n"),
                                Text(resp_data["error_message"]),
                            ]
                        )
                    )
                )
