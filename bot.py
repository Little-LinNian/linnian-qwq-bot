import asyncio
import os
import aiohttp
import avilla
from avilla.entity import EntityPtr
import uvicorn
from lib import token as tku
import api
import ujson
from avilla.execution.fetch import FetchStranger
from avilla import Avilla
from avilla.builtins.elements import Image, PlainText
from avilla.builtins.profile import GroupProfile, MemberProfile, StrangerProfile
from avilla.event.message import MessageEvent
from avilla.execution.message import MessageSend
from avilla.message.chain import MessageChain
from avilla.network.clients.aiohttp import AiohttpWebsocketClient
from avilla.onebot.config import OnebotConfig, WebsocketCommunication
from avilla.onebot.protocol import OnebotProtocol
from avilla.provider import RawProvider
from avilla.relationship import Relationship
from lib import img2text
from graia.broadcast import Broadcast
from graia.saya import Saya
from graia.saya.builtins.broadcast import BroadcastBehaviour
from loguru import logger
from pathlib import Path
from yarl import URL
import aiofiles

from lib.config import get_config, set_config_path
from lib.draw import prts_handle

set_config_path("config.yml")
logger.add("bot.log")

logger.add("./cache/debuglogs", level="DEBUG")
loop = asyncio.get_event_loop()
bcc = Broadcast(loop=loop)
loop.run_until_complete(prts_handle.init_prts_data())
saya = Saya(broadcast=bcc)
saya.install_behaviours(BroadcastBehaviour(bcc))
TICKET = False
with saya.module_context():
    saya.require("module.sign_in")
    saya.require("module.rua")
    saya.require("module.draw_prts")
    saya.require("module.ATM")
    saya.require("module.img2link")
    saya.require("module.two_in_one")
    saya.require("module.prme")
    saya.require("module.longtu")
    #saya.require("module.yingyu")
    saya.require("module.5000zhao")
    saya.require("module.cloudbuilder")
    saya.require("module.rss")
session = aiohttp.ClientSession(loop=loop)
app = Avilla(
    bcc,
    OnebotProtocol,
    {"ws": AiohttpWebsocketClient(session)},
    {
        OnebotProtocol: OnebotConfig(
            access_token="",
            bot_id=2747804982,
            communications={
                "ws": WebsocketCommunication(api_root=URL("ws://localhost:6700/"))
            },
        )
    },
    logger=logger
)




@bcc.receiver(MessageEvent)
async def menu(event: MessageEvent, rs: Relationship):
    if event.message.as_display() == "#菜单":
        async with aiofiles.open("menu.txt", mode="r",encoding="utf-8") as f:
            menu = await f.read()
        resp = await asyncio.to_thread( img2text.create_image,text=menu)
        await rs.exec(
            MessageSend(MessageChain.create([Image(RawProvider(resp))]))
        )


@bcc.receiver(MessageEvent)
async def saya_manager(event: MessageEvent, rs: Relationship[MemberProfile,GroupProfile]):
    cfg = await get_config()
    if not rs.ctx.profile.group.id not in cfg["ADMIN"]:
        return
    if not event.message.as_display().startswith("#mods "):
        return
    msg = event.message.as_display()[6:].split(" ")
    if msg[0] == "uninstall":
        module = msg[1]
        try:
            saya.uninstall_channel(saya.channels.get(module))
            await rs.exec(
                MessageSend(
                    MessageChain.create(
                        [PlainText("Module {} has been uninstalled".format(module))]
                    )
                )
            )
        except Exception as e:
            await rs.exec(
                MessageSend(
                    MessageChain.create(
                        [
                            PlainText(
                                "Module {} cannot be uninstalled,Because {}".format(
                                    module, str(e)
                                )
                            )
                        ]
                    )
                )
            )
    if msg[0] == "install":
        module = msg[1]
        try:
            with saya.module_context():
                saya.require(module)
            await rs.exec(
                MessageSend(
                    MessageChain.create(
                        [PlainText("Module {} has been installed".format(module))]
                    )
                )
            )
        except Exception as e:
            await rs.exec(
                MessageSend(
                    MessageChain.create(
                        [
                            PlainText(
                                "Module {} cannot be installed,Because {}".format(
                                    module, str(e)
                                )
                            )
                        ]
                    )
                )
            )
    if msg[0] == "reload":
        module = msg[1]
        try:
            with saya.module_context():
                saya.reload_channel(saya.channels.get(module))
            await rs.exec(
                MessageSend(
                    MessageChain.create(
                        [PlainText("Module {} has been reloaded".format(module))]
                    )
                )
            )
        except Exception as e:
            await rs.exec(
                MessageSend(
                    MessageChain.create(
                        [
                            PlainText(
                                "Module {} cannot be reloaded,Because {}".format(
                                    module, str(e)
                                )
                            )
                        ]
                    )
                )
            )
    if msg[0] == "now":
        msg = ""
        for i in saya.channels.keys():
            msg += f"{i} "
        await rs.exec(MessageSend(MessageChain.create([PlainText(msg)])))

@bcc.receiver(MessageEvent)
async def token_g(event: MessageEvent, rs: Relationship[MemberProfile,GroupProfile]):
    cfg = await get_config()
    if not rs.ctx.profile.group.id not in cfg["ADMIN"]:
        return
    if  event.message.as_display() == "#面板token":
        token = await tku.get_token(32)
        async with aiofiles.open("token.json", mode="r",encoding="utf-8") as f:
            try:
                data = ujson.loads(await f.read())
            except:
                data = {}
            data[rs.ctx.id] = token
            async with aiofiles.open("token.json", mode="w",encoding="utf-8") as f:
                await f.write(ujson.dumps(data))
            await rs.exec(
                MessageSend(
                    MessageChain.create([PlainText("已经获取到token，请查看私聊")]),
                )
            )
            await app.protocol._ws_client_send_packet("send_private_msg", {
                "user_id": rs.ctx.id,
                "message": token,
                "auto_escape": True
            })


api_launched = False
@bcc.receiver(MessageEvent)
async def on_launch():
    global api_launched
    if api_launched:
        return
    api_launched = True
    app.logger.debug("Try to launch api")
    api.saya = saya

    api.avilla = app
    await asyncio.to_thread(uvicorn.run, app=api.app, host="0.0.0.0", port=7050)
try:
    app.launch_blocking()
except KeyboardInterrupt:
    quit()
 
