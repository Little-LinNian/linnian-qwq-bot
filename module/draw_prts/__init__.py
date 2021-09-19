import asyncio
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from avilla.core.execution.message import MessageSend
from avilla.core.message.chain import MessageChain
from avilla.core.relationship import Relationship
from avilla.core.builtins.profile import MemberProfile, GroupProfile
from avilla.core.builtins.elements import Text, Notice
from avilla.core.builtins.elements import Image as IMG
from avilla.core.event.message import MessageEvent
from lib import limiter
from lib.draw import prts_handle
from lib import bank

bank = bank.Bank("./data/bank.json")
saya = Saya.current()
channel = Channel.current()


@channel.use(ListenerSchema(listening_events=[MessageEvent]))
async def sendmsg(event: MessageEvent, rs: Relationship):
    if event.message.as_display() == "#方舟单抽":

        await limiter.limit("draw_prts", rs, 4)
        try:
            await rs.exec(MessageSend(MessageChain.create([Text("qwq 将消耗6霖念币")])))
            await asyncio.sleep(2)
            await bank.withdraw(rs.ctx.id, 6)
        except Exception as e:
            await rs.exec(
                MessageSend(
                    MessageChain.create([Text("qwq 消耗6霖念币失败，错误信息：{}".format(e))])
                )
            )
            return

        resp = await prts_handle.prts_draw(1)
        await rs.exec(MessageSend(MessageChain.create([Notice(target=event.ctx.id)])))
        await asyncio.sleep(2)
        await rs.exec(MessageSend(resp))
    elif event.message.as_display() == "#方舟十连":
        await limiter.limit("draw_prts_10", rs, 6)
        try:
            await rs.exec(
                MessageSend(
                    MessageChain.create([Text("qwq 将消耗60霖念币")]),
                )
            )
            await asyncio.sleep(2)
            await bank.withdraw(rs.ctx.id, 60)
        except Exception as e:
            await rs.exec(
                MessageSend(
                    MessageChain.create([Text("qwq 消耗60霖念币失败，错误信息：{}".format(e))])
                )
            )
            return

        resp = await prts_handle.prts_draw(10)
        await rs.exec(MessageSend(MessageChain.create([Notice(target=event.ctx.id)])))
        await asyncio.sleep(2)
        await rs.exec(MessageSend(resp))
