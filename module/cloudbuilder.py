from pathlib import Path
import aiohttp
import re
import os
import asyncio
from avilla.builtins.profile  import GroupProfile, MemberProfile
from avilla.builtins.elements import Image, PlainText
from avilla.event.message import MessageEvent
from avilla.provider import RawProvider
from avilla.relationship import Relationship
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from avilla.message.chain import MessageChain
from avilla.exceptions import AccountMuted
from lib import img2text, limiter
from avilla.execution.message import MessageSend

# 插件信息
__name__ = "NetworkCompiler"
__description__ = "网络编译器（菜鸟教程）"
__author__ = "SAGIRI-kawaii"+" RainLong"
__usage__ = "在群内发送 #编译 语言:\\n代码 即可"

saya = Saya.current()
channel = Channel.current()

channel.name(__name__)
channel.description(f"{__description__}\n使用方法：{__usage__}")
channel.author(__author__)


@channel.use(ListenerSchema(
    listening_events=[MessageEvent]
    )
)
async def network_compiler(
        event: MessageEvent,
        rs: Relationship[MemberProfile,GroupProfile]
):
    message_text = event.message.as_display()
    if not message_text.startswith("#编译 "):
        return
    await limiter.group_limit("cb",rs,10)
    language = re.findall(r"#编译 (.*?):", message_text, re.S)[0]
    code = message_text[6 + len(language):]
    result = await network_compile(language, code)
    print(result)
    try:
        if isinstance(result, str):
            
            resp = await asyncio.to_thread( img2text.create_image,text=result)
            await rs.exec(MessageSend(MessageChain.create([Image(RawProvider(resp))])))
        else:
            if len(result["output"]) > 50:
                
                result["output"] = result["output"][:50]
            if len(result["errors"]) > 50:
                result["errors"] = result["errors"][:50]
            resp = await  asyncio.to_thread( img2text.create_image,text=f'{result["output"] if result["output"] else result["errors"]}\n由菜鸟教程提供API')
            await rs.exec(MessageSend( MessageChain.create([Image(RawProvider(resp))])))
    except AccountMuted:
        pass


legal_language = {
    "R": 80,
    "vb": 84,
    "ts": 1001,
    "kt": 19,
    "pas": 18,
    "lua": 17,
    "node.js": 4,
    "go": 6,
    "swift": 16,
    "rs": 9,
    "sh": 11,
    "pl": 14,
    "erl": 12,
    "scala": 5,
    "cs": 10,
    "rb": 1,
    "cpp": 7,
    "c": 7,
    "java": 8,
    "py3": 15,
    "py": 0,
    "php": 3
}


async def network_compile(language: str, code: str):
    if language not in legal_language:
        return f"支持的语言：{', '.join(list(legal_language.keys()))}"
    url = "https://tool.runoob.com/compile2.php"
    payload = {
        "code": code,
        "token": "4381fe197827ec87cbac9552f14ec62a",
        "stdin": "",
        "language": legal_language[language],
        "fileext": language
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url=url, headers=headers, data=payload) as resp:
            res = await resp.json()
    return {
        "output": res["output"],
        "errors": res["errors"]
    }