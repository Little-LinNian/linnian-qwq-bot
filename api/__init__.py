import asyncio
import datetime
import os
import platform
import socket
import sys
import ujson
import aiofiles
from .code_get import get_code
import psutil
from avilla.core import Avilla
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from graia.saya import Saya


start_time = datetime.datetime.now()
saya: Saya
avilla: Avilla
avilla_v = os.popen("pip show avilla-core").readlines()[1].split(" ")[1]


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
uninstall_modules =  {}


@app.get("/")
async def root():
    return {"message": "Hello, World!"}


@app.get("/saya/install")
async def install_saya_module(name: str,token: str):
    async with aiofiles.open("token.json", mode="r") as f:
        data = ujson.loads(await f.read())
    if not token in data.values():
        return {"status": "ERROR", "message": "Invalid Token"}

    try:
        if name in uninstall_modules:
            del uninstall_modules[name]
        with saya.module_context():
            saya.require(name)
        return {"status": "OK"}
    except Exception as e:
        return {"status": "FAIL", "reason": str(e)}


@app.get("/saya/uninstall")
async def uninstall_saya_module(name: str,token: str):
    async with aiofiles.open("token.json", mode="r") as f:
        data = ujson.loads(await f.read())
    if not token in data.values():
        return {"status": "ERROR", "message": "Invalid Token"}
    try:
        channel = saya.channels.get(name)
        saya_name = name
        channel_name = channel._name
        description = channel._description
        author = ""
        for i in   channel._author:
            author += i+" "
        module = {"SayaName": saya_name, "ChannelName": channel_name, "description": description, "author": author}  
        saya.uninstall_channel(channel)
        uninstall_modules[name] = module
        return {"status": "OK"}
    except Exception as e:
        return {"status": "FAIL", "reason": str(e)}


@app.get("/saya/list/disable")
async def list_uninstall_module():
    _uninstall_modules = []
    for i in uninstall_modules.values():
        _uninstall_modules.append(i)

    return {"status": "OK", "modules": _uninstall_modules}


@app.get("/saya/list")
async def list_saya_module():
    modules = []
    for name, channel in saya.channels.items():
        saya_name = name
        channel_name = channel._name
        description = channel._description
        author = ""
        for i in   channel._author:
            author += i+" "
        modules.append({"SayaName": saya_name, "ChannelName": channel_name, "description": description, "author": author})
    return {"status": "OK", "modules": modules}




def get_sys_info_sync():

    def get_host_ip():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        finally:
            s.close()
        return ip
    mem = psutil.virtual_memory()
    cpu_percent = psutil.cpu_percent(interval=1)
    mem_percent = mem.percent
    cpu_count = psutil.cpu_count()
    cpu_name = platform.processor()
    avilla_version = avilla_v
    sys_name = platform.version()
    sys_pl = platform.system()
    total_mem = str(psutil.virtual_memory().total/1024/1024)+"M"
    net = psutil.net_io_counters()
    net_sent = net.bytes_sent/1024/1024
    net_recv = net.bytes_recv/1024/1024
    ip = get_host_ip()
    return {"status": "OK",
            "CPUH": cpu_count,
            "CPUName": cpu_name,
            "OSSName": sys_name, "OS": sys_pl,
            "MMInfo": total_mem, "IP": ip,
            "AvillaVersion": avilla_version,
            "AvillaProtocol": str(avilla.protocol.platform.name+" "+avilla.protocol.platform.implementation+" "+avilla.protocol.platform.supported_impl_version),
            "Plugins": len(saya.channels.keys()),
            "PythonVersion": sys.version[:5],

            "UPtime": str(start_time.year)+"-"+str(start_time.month)+"-"+str(start_time.day)+" "+str(start_time.hour)+":"+str(start_time.minute)+":"+str(start_time.second),
            "SystemUsage": {"CpuUsage": str(cpu_percent),
                            "MemUsage": str(mem_percent),
                            "NetSend": net_sent,
                            "NetRecv": net_recv
                            },
            }


@app.websocket("/sys/info/ws")
async def get_sys_info(ws: WebSocket):

    await ws.accept()

    try:
        while True:
            resp = await asyncio.to_thread(get_sys_info_sync)
            await ws.send_json(resp)
            await asyncio.sleep(1)

    except WebSocketDisconnect:
        await ws.close()


@app.websocket("/logs")
async def get_logs(ws: WebSocket):
    await ws.accept()
    try:

            while True:
                async with aiofiles.open("./cache/debuglogs") as f:
                    debuglogs = await f.readlines()            
                debuglog = debuglogs[len(debuglogs) -1]
                await ws.send_text(debuglog)
    except WebSocketDisconnect:
        await ws.close()

@app.get("/getcode")
async def get_code_from_url(name: str,token: str):
    async with aiofiles.open("token.json", mode="r") as f:
        data = ujson.loads(await f.read())
    if not token in data.values():
        return {"status": "ERROR", "message": "Invalid Token"}
    code = await get_code(name)
    return  {"status": "OK","code": code}
