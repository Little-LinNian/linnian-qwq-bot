import asyncio
from coscmd.cos_client import CoscmdConfig, Interface
from . import config as ucf
from pathlib import Path


async def getcfg() -> CoscmdConfig:

    config = await ucf.get_config()
    cfg = CoscmdConfig(
        config["appid"],
        config["region"],
        None,
        config["bucket"],
        config["secret_id"],
        config["secret_key"],
    )
    return cfg


async def upload_file(file: Path, auth_user: int) -> str:
    cfg = await getcfg()
    iterf = Interface(cfg)
    iterf.upload_file(
        str(file.absolute()),
        str(auth_user) + "/" + file.name,
        skipmd5=False,
        include="*",
        ignore="",
        sync=False,
    )
    print(cfg.uri() + str(auth_user) + "/" + f"{file.name}")
    return "https://link.linnian.icu/" + str(auth_user) + "/" + f"{file.name}"


async def del_file(file: Path, auth_user) -> str:
    cfg = await getcfg()
    iterf = Interface(cfg)
    iterf.delete_file(
        str(auth_user) + "/" + file.name, force=True, yes=True, versionId=""
    )
