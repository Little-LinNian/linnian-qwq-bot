from avilla.core.builtins.elements import Text
from avilla.core.builtins.profile import GroupProfile, MemberProfile
from avilla.core.event.message import MessageEvent
from avilla.core.execution.message import MessageSend
from avilla.core.message.chain import MessageChain
from avilla.core.relationship import Relationship
from graia.saya import Channel, Saya
from lib.yinglish import yinglish
from graia.saya.builtins.broadcast.schema import ListenerSchema

saya = Saya.current()
channel = Channel.current()


@channel.use(ListenerSchema(listening_events=[MessageEvent]))
async def handle_message(
    event: MessageEvent, rs: Relationship
):
    if not event.message.as_display().startswith("#变坏 "):
        return
    msg = event.message.as_display()[4:]
    resp = yinglish.chs2yin(msg, 1.0)
    await rs.exec(MessageSend(MessageChain.create([Text(resp)])))
