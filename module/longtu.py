from os import write
from avilla.provider import HttpGetProvider
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from avilla.execution.message import MessageSend
from avilla.message.chain import MessageChain
from avilla.relationship import Relationship
from avilla.builtins.profile import MemberProfile, GroupProfile
from avilla.builtins.elements import PlainText, Notice
from avilla.builtins.elements import Image
from avilla.event.message import MessageEvent
from lib.bank import Bank
from lib.limiter import limit
import aiohttp

saya = Saya.current()
channel = Channel.current()


@channel.use(ListenerSchema(listening_events=[MessageEvent]))
async def message_event_logger(event: MessageEvent, rs: Relationship[MemberProfile,GroupProfile]):
    if event.message.as_display() == "来点龙图" and rs.ctx.profile.group.id == "1067987419":
        await rs.exec(
            MessageSend(
                MessageChain.create(
                    [Image(HttpGetProvider("https://lt.linnian.icu/api/get"))]
                )
            )
        )
