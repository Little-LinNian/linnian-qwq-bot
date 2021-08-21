from pathlib import Path
from avilla.builtins.profile import GroupProfile, MemberProfile
from avilla.message.chain import MessageChain
from avilla.builtins.elements import PlainText
from avilla.builtins.elements import Image
from asyncio import to_thread
from lib.limiter import group_limit
from avilla.event.message import MessageEvent
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from avilla.exceptions import AccountMuted
from avilla.execution.message import MessageSend
from avilla.relationship import Relationship


from .utils import genImage

# 插件信息
__name__ = "5000M"
__description__ = "一个可以生成 5000M 的插件"
__author__ = "SAGIRI-kawaii(V4)"
__usage__ = "发送 `#5000兆 text1 text2` 即可"

saya = Saya.current()
channel = Channel.current()

channel.name(__name__)
channel.description(f"{__description__}\n使用方法：{__usage__}")
channel.author(__author__)
channel.author("LinNian(V5)")


@channel.use(ListenerSchema(
    listening_events=[MessageEvent]
))
async def pornhub_style_logo_generator(
    event: MessageEvent,
    rs: Relationship[MemberProfile,GroupProfile]
):
    if not event.message.as_display().startswith("#5000兆 "):
        return
    await group_limit("5000M",rs,15)
    try:
        message = event.message
        _, left_text, right_text = message.as_display().split(" ")
        if message.has(Image):
            await rs.exec(MessageSend(MessageChain.create([PlainText(text="不支持的内容！不要给我一些稀奇古怪的东西！")])))
            return
        try:
            try:
                await to_thread( genImage(word_a=left_text, word_b=right_text).save,"./data/5000zhao/test.png")
            except TypeError:
                await rs.exec(MessageSend(MessageChain.create([PlainText(text="不支持的内容！不要给我一些稀奇古怪的东西！")])))
                return None
            await rs.exec(MessageSend( MessageChain.create([Image.fromLocalFile(Path("./data/5000zhao/test.png"))])))
        except AccountMuted:
            pass
    except ValueError:
        try:
            await rs.exec(MessageSend( MessageChain.create([PlainText(text="参数非法！使用格式：5000兆 text1 text2")])))
        except AccountMuted:
            pass
