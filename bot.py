from pathlib import Path
import aiohttp
from lib.bank import Bank
from avilla.execution.message import MessageSend
from avilla.message.chain import MessageChain
from avilla.onebot.config import OnebotConfig, WebsocketCommunication
from avilla.relationship import Relationship
from avilla.builtins.elements import Image, PlainText
from graia.broadcast import Broadcast
from avilla import Avilla
from avilla.onebot.protocol import OnebotProtocol
from avilla.network.clients.aiohttp import AiohttpWebsocketClient
from avilla.onebot.protocol import OnebotProtocol
from avilla.event.message import MessageEvent
import asyncio
from lib.draw import prts_handle
from loguru import logger
from graia.saya import Saya
from graia.saya.builtins.broadcast import BroadcastBehaviour
from yarl import URL

loop = asyncio.get_event_loop()
loop.run_until_complete(prts_handle.init_prts_data())
bcc = Broadcast(loop=loop)
saya = Saya(broadcast=bcc)
saya.install_behaviours(BroadcastBehaviour(bcc))
with saya.module_context():
   saya.require("module.sign_in")
   saya.require("module.rua")
   saya.require("module.draw_prts")
   saya.require("module.ATM")
session = aiohttp.ClientSession(loop=loop)
app = Avilla(bcc, OnebotProtocol, {
    "ws": AiohttpWebsocketClient(session)} ,
    {
        OnebotProtocol: OnebotConfig(
            access_token = "",
            bot_id=2747804982,
            communications = {
                "ws": WebsocketCommunication(api_root=URL("ws://localhost:6700/"))
            }
        )
    }
)

@bcc.receiver(MessageEvent)
async def message_event_logger(event: MessageEvent):
    if  not event.ctx.profile.group:
        return
    
    group = event.ctx.profile.group.id
    group_name = event.ctx.profile.group.profile.name
    member = event.ctx.id
    member_name = event.ctx.profile.name
    logger.success(f"[From Group(id: {group} name: {group_name}) Member(id: {member} name: {member_name}) MSG: {event.message.as_display()}]")

@bcc.receiver(Exception)
async def exception_logger(exception: Exception):
    logger.exception(str(exception))

app.launch_blocking()