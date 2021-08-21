import string
import random 




async def get_token(length: int = 8) -> str:
    """
    生成token
    :param length: token长度
    :return: token
    """
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))