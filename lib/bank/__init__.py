import asyncio
from os import write
import ujson
from pathlib import Path
import time
import aiofiles


class Bank:
    '''银行系统'''

    def __init__(self, file: str):
        self.file = file

    async def save(self, data):

        async with aiofiles.open(self.file, 'w') as f:
            await f.write(ujson.dumps(data))

    async def load(self):

        async with aiofiles.open(self.file, 'r') as f:
            return ujson.loads(await f.read())

    
    async def ensure_account(self, account: str) -> bool:
        '''确保账号存在'''
        data = await self.load()
        if account in data:
            return True
        else:
            return False
    
    async def _ensure_account(self, account: str):
        '''确保账号存在'''
        data = await self.load()
        if not account in data:
            raise ValueError('账号未存在')

    async def create_account(self, account: str, initial_balance: int):
        '''创建账号'''
        data = await self.load()
        if account in data:
            raise ValueError('账号已存在')
        data[account] = {'balance': initial_balance}
        await self.save(data)

    async def remove_account(self, account: str):
        '''移除账号'''
        data = await self.load()
        if not account in data:
            raise ValueError('账号未存在')
        del data[account]
        await self.save(data)

    async def get_balance(self, account: str):
        '''获得余额'''
        await self._ensure_account(account)
        data = await self.load()
        return data[account]['balance']

    async def deposit(self, account: str, amount: int):
        '''存款'''
        await self._ensure_account(account)
        data = await self.load()
        data[account]['balance'] += amount
        await self.save(data)

    async def withdraw(self, account: str, amount: int):
        '''取款'''
        await self._ensure_account(account)
        data = await self.load()
        if data[account]['balance'] >= amount:
            data[account]['balance'] -= amount
            await self.save(data)
        else:
            raise ValueError('余额不足')

    async def transfer(self, account_from: str, account_to: str, amount: int):
        '''转账'''
        await self._ensure_account(account_from)
        await self._ensure_account(account_to)
        data = await self.load()
        if data[account_from]['balance'] >= amount:
            data[account_from]['balance'] -= amount
            data[account_to]['balance'] += amount
            await self.save(data)
        else:
            raise ValueError('余额不足')

