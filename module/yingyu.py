from avilla.builtins.elements import PlainText
from avilla.builtins.profile import GroupProfile, MemberProfile
from avilla.event.message import MessageEvent
from avilla.execution.message import MessageSend
from avilla.message.chain import MessageChain
from avilla.relationship import Relationship
from graia.saya import Channel, Saya
from lib.yinglish import yinglish
from graia.saya.builtins.broadcast.schema import ListenerSchema

saya = Saya.current()
channel = Channel.current()


@channel.use(ListenerSchema(listening_events=[MessageEvent]))
async def handle_message(
    event: MessageEvent, rs: Relationship[MemberProfile, GroupProfile]
):
    if not event.message.as_display().startswith("#变坏 "):
        return
    msg = event.message.as_display()[4:]
    resp = yinglish.chs2yin(msg, 1.0)
    await rs.exec(MessageSend(MessageChain.create([PlainText(resp)])))
