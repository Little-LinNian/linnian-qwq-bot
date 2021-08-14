from os import write
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
async def message_event_logger(event: MessageEvent,rs: Relationship):
    if event.message.as_display() == "舔我":
        await limit("prme",rs,8)
        async with aiohttp.ClientSession() as session:
            async with session.get("https://chp.shadiao.app/api.php") as resp:
                data = await resp.text()
        await rs.exec(
            MessageSend(
                MessageChain.create(
                    [Notice(target=rs.ctx.id),PlainText(" "+data)]
                )
            )
        )
