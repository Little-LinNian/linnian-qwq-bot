import asyncio
from loguru import logger

import os


from .prts_handle import update_prts_info, init_prts_data
from .config import DRAW_PATH, PRTS_FLAG


async def async_update_game():
    tasks = []
    init_lst = [init_prts_data]
    if PRTS_FLAG and not os.path.exists(DRAW_PATH + "prts.json"):
        tasks.append(asyncio.ensure_future(update_prts_info()))
        init_lst.remove(init_prts_data)

    try:
        await asyncio.gather(*tasks)
        for func in init_lst:
            await func()
    except asyncio.exceptions.CancelledError:
        logger.warning("更新异常：CancelledError，再次更新...")
        await async_update_game()


asyncio.run(async_update_game())
