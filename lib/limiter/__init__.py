import time
from avilla.core.execution.message import MessageSend
from avilla.core.message.chain import MessageChain
from avilla.core.relationship import Relationship
from avilla.core.builtins.elements import Notice, Text
from graia.broadcast import ExecutionStop
from avilla.core.builtins.profile import MemberProfile, GroupProfile
from loguru import logger


BLOCK_DICT = {}


async def limit(name: str, rs: Relationship, sleep_time: int):
    name = name + f"_{rs.ctx.id}"
    time_now = int(time.time())

    if name in BLOCK_DICT:
        time_last = BLOCK_DICT[name]
        if not time_now - time_last > sleep_time:
            await rs.exec(
                MessageSend(
                    MessageChain.create(
                        [
                            Notice(target=rs.ctx.id),
                            Text(f"你使用的这个功能已被暂停{sleep_time}，请稍后 awa，我也只提醒一次"),
                        ]
                    )
                )
            )
            time_last = BLOCK_DICT[name]
            del BLOCK_DICT[name]
            BLOCK_DICT[name + "_no"] = time_last
            raise ExecutionStop()
    block_name = name + "_no"
    if block_name in BLOCK_DICT:
        time_last = BLOCK_DICT[block_name]
        if not time_now - time_last > sleep_time:
            del BLOCK_DICT[block_name]
            raise ExecutionStop()
    BLOCK_DICT[name] = time_now
    logger.info(f"{name} Stopped")

async def group_limit(name: str, rs: Relationship, sleep_time: int):
    name = name + f"_{rs.ctx.profile.group.id}"
    time_now = int(time.time())
    if name in BLOCK_DICT:
        time_last = BLOCK_DICT[name]
        if not time_now - time_last > sleep_time:
            await rs.exec(
                MessageSend(
                    MessageChain.create(
                        [
                            Notice(target=rs.ctx.profile.group.id),
                            Text(f"此群的这个功能已被暂停{sleep_time}，请稍后 awa，我也只提醒一次"),
                        ]
                    )
                )
            )
            time_last = BLOCK_DICT[name]
            del BLOCK_DICT[name]
            BLOCK_DICT[name + "_no"] = time_last
            raise ExecutionStop()
    block_name = name + "_no"
    if block_name in BLOCK_DICT:
        time_last = BLOCK_DICT[block_name]
        if not time_now - time_last > sleep_time:
            del BLOCK_DICT[block_name]
            raise ExecutionStop()
    BLOCK_DICT[name] = time_now
    logger.info(f"{name} Stopped")
