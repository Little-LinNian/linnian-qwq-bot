import asyncio
from pathlib import Path
from lib import img2text
import feedparser
import aiohttp

async def lofter_parser(rss_url: str) -> bytes:
    async with aiohttp.request("Get",rss_url) as f:
        resp = feedparser.parse(await f.read())
    resp  = resp["channel"]
    title = resp["title"]
    link = resp["links"][0]["href"]
    subtitle = resp["subtitle"]
    updated_parsed = resp["updated_parsed"]
    result  = f"Lofter Report\n作者:\n{title}\n主页:\n{link}\n签名:\n{subtitle}\n最后更新时间:\n{updated_parsed.tm_year}-{updated_parsed.tm_mon}-{updated_parsed.tm_mday}\n{updated_parsed.tm_hour}:{updated_parsed.tm_min}:{updated_parsed.tm_sec}"
    resp = await asyncio.to_thread(img2text.create_image,text=result)
    return await resp