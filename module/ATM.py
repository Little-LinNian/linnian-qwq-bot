from pathlib import Path
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

from avilla.core.execution.message import MessageSend
from avilla.core.message.chain import MessageChain
from avilla.core.relationship import Relationship
from avilla.core.builtins.profile import MemberProfile, GroupProfile
from avilla.core.builtins.elements import Text, Notice
from avilla.core.builtins.elements import Image as IMG
from avilla.core.event.message import MessageEvent
from lib.bank import Bank
from lib import limiter

saya = Saya.current()
channel = Channel.current()
bank = Bank("./data/bank.json")


@channel.use(ListenerSchema(listening_events=[MessageEvent]))
async def sendmsg(event: MessageEvent, rs: Relationship):
    if event.message.as_display().startswith("#储蓄罐 "):
        await limiter.limit("ATM", rs, 5)
        msg = event.message.get_first(Text).text[5:]
        if msg == "注册":
            try:
                await bank.create_account(rs.ctx.id, 100)
                await rs.exec(
                    MessageSend(MessageChain.create([Text("注册霖念储蓄罐成功 w~")]))
                )
            except Exception as e:
                await rs.exec(
                    MessageSend(
                        MessageChain.create([Text(f"注册霖念储蓄罐失败 原因是{e} qaq")])
                    )
                )
        elif msg.startswith("充值 ") and event.message.has(Notice):
            if not rs.ctx.id == "2544704967":
                await rs.exec(
                    MessageSend(
                        MessageChain.create([Text("您不是霖念储蓄罐的管理员，无权进行此操作qwq")])
                    )
                )
                return
            money = int(msg[3:])

            try:
                if money < 0 or money > 10000:
                    await rs.exec(
                        MessageSend(
                            MessageChain.create([Text("充值金额超出范围(0-10000)，请重新输入")])
                        )
                    )
                    return
                await bank.deposit(event.message.get_first(Notice).target, money)
                await rs.exec(MessageSend(MessageChain.create([Text("充值成功!Owo")])))
            except Exception as e:
                await rs.exec(
                    MessageSend(MessageChain.create([Text(f"充值失败 原因是{e} qaq")]))
                )
        elif msg == "查询":
            try:
                await rs.exec(
                    MessageSend(
                        MessageChain.create(
                            [
                                Text(
                                    f"你的储蓄罐余额为{await bank.get_balance(rs.ctx.id)}霖念币 Owo"
                                )
                            ]
                        )
                    )
                )
            except Exception as e:
                await rs.exec(
                    MessageSend(MessageChain.create([Text(f"查询失败 原因是{e} qwq")]))
                )
        elif msg.startswith("转账 ") and event.message.has(Notice):
            toid = event.message.get_first(Notice).target
            try:
                money = int(msg[3:])
                if money < 0 or money > 10000:
                    await rs.exec(
                        MessageSend(
                            MessageChain.create([Text("转账金额超出范围(0-10000)，请重新输入")])
                        )
                    )
                    return
                await bank.transfer(rs.ctx.id, toid, int(money))
                await rs.exec(MessageSend(MessageChain.create([Text("转账成功!OwO")])))
            except Exception as e:
                await rs.exec(
                    MessageSend(MessageChain.create([Text(f"转账失败 原因是{e} qwq")]))
                )
