from os import write
from avilla.core.provider import HttpGetProvider
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from avilla.core.execution.message import MessageSend
from avilla.core.message.chain import MessageChain
from avilla.core.relationship import Relationship
from avilla.core.builtins.profile import MemberProfile, GroupProfile
from avilla.core.builtins.elements import Text, Notice
from avilla.core.builtins.elements import Image
from avilla.core.event.message import MessageEvent
from lib.bank import Bank
from lib.limiter import limit
import aiohttp

saya = Saya.current()
channel = Channel.current()


@channel.use(ListenerSchema(listening_events=[MessageEvent]))
async def message_event_logger(event: MessageEvent, rs: Relationship):
    if event.message.as_display() == "来点龙图" and rs.ctx.profile.group.id == "1067987419":
        await rs.exec(
            MessageSend(
                MessageChain.create(
                    [Image(HttpGetProvider("https://lt.linnian.icu/api/get"))]
                )
            )
        )
