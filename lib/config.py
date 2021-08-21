import yaml
import aiofiles


def set_config_path(path: str):
    global CONFIG_PATH
    CONFIG_PATH = path


async def get_config() -> dict:
    async with aiofiles.open(CONFIG_PATH, "r") as f:
        return yaml.load(await f.read(), Loader=yaml.SafeLoader)


async def save_config(config: dict):
    async with aiofiles.open(CONFIG_PATH, "w") as f:
        await f.write(yaml.dump(config, Dumper=yaml.SafeDumper))
