ABLE = False
from pathlib import Path
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
import random
from avilla.execution.message import MessageSend
from avilla.message.chain import MessageChain
from avilla.relationship import Relationship
from avilla.builtins.profile import MemberProfile, GroupProfile
from avilla.builtins.elements import PlainText, Notice
from avilla.builtins.elements import Image as IMG
from avilla.event.message import MessageEvent
from lib.bank import Bank
from lib import limiter

saya = Saya.current()
channel = Channel.current()
bank = Bank("./data/bank.json")
tickets = {}
ticket_list = []
last_result = {}


@channel.use(ListenerSchema(listening_events=[MessageEvent]))
async def sendmsg(event: MessageEvent, rs: Relationship[MemberProfile, GroupProfile]):
    if event.message.as_display().startswith("#许愿券 "):
        await limiter.limit("wish", rs, 12)
        ctx = event.message.get_first(PlainText).text[5:]
        if ctx.startswith("购买 "):
            ticketnumber = str(int(ctx[3:]))
            if len(tickets) == 5:
                await rs.exec(
                    MessageSend(
                        MessageChain.create([PlainText("许愿券超过5张了UWU，请发送#许愿券 开奖")])
                    )
                )
                pass
            if int(ticketnumber) < 0:
                await rs.exec(
                    MessageSend(MessageChain.create([PlainText("不能为负数哦 UwU")]))
                )
                pass
            elif not len(ticketnumber) == 6:
                await rs.exec(
                    MessageSend(MessageChain.create([PlainText("许愿券码为6位数 UwU")]))
                )
                pass

            elif rs.ctx.id in tickets.keys():
                await rs.exec(
                    MessageSend(MessageChain.create([PlainText("你已经购买了哦 UwU")]))
                )
                pass
            elif ticketnumber in tickets.values():
                await rs.exec(
                    MessageSend(MessageChain.create([PlainText("已经被人购买了哦 UwU")]))
                )
                pass

            else:
                try:
                    await bank.withdraw(rs.ctx.id, 6)
                    tickets[rs.ctx.id] = ticketnumber
                    ticket_list.append(rs.ctx.id)
                    await rs.exec(
                        MessageSend(
                            MessageChain.create(
                                [
                                    PlainText(
                                        f"许愿券购买成功，现在共有{len(tickets)} 张许愿券，到第5张许愿券开奖"
                                    )
                                ]
                            )
                        )
                    )
                except ValueError:
                    await rs.exec(
                        MessageSend(MessageChain.create([PlainText("余额不足哦 UwU")]))
                    )
        if ctx.startswith("开奖"):
            if len(tickets) != 5:
                await rs.exec(
                    MessageSend(MessageChain.create([PlainText("许愿券还没有开奖 UwU")]))
                )
            else:

                ticket = random.choice(ticket_list)
                ticket_num = tickets[ticket]
                jid = len(last_result.keys())
                await rs.exec(
                    MessageSend(
                        MessageChain.create(
                            [
                                PlainText(
                                    "中奖许愿券为{} UwU，本次抽奖id为{}".format(ticket_num, jid)
                                )
                            ]
                        )
                    )
                )
                try:
                    await bank.deposit(id, 60)
                except:
                    await bank.create_account(id, 160)
                await rs.exec(
                    MessageSend(MessageChain.create([PlainText("已向许愿成功的人转入60霖念币")]))
                )
                last_result[jid] = "id为{}中奖许愿券为{} UwU".format(jid, ticket_num)
                tickets.clear()
        if ctx.startswith("查询 "):
            jid = int(ctx[3:])
            await rs.exec(
                MessageSend(MessageChain.create([PlainText(last_result[jid])]))
            )
