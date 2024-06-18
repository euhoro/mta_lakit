import os
import time
import uuid
import aioredis
import asyncio
from common import InventoryService, Inventory


class RedisInventoryServiceAsync(): #InventoryService):
    def __init__(self, client, lock_name='inventory_lock', lock_timeout=10):
        self.client = client
        self.lock_name = lock_name
        self.lock_timeout = lock_timeout
        self.lock_value = str(uuid.uuid4())
        self.initial_inventory = Inventory(
            BILL={200.0: 7, 100.0: 4, 20.0: 15},
            COIN={10.0: 10, 1.0: 10, 5.0: 1, 0.1: 12, 0.01: 21}
        )

    async def read_inventory(self) -> Inventory:
        inventory_json = await self.client.get('atm_inventory')
        if inventory_json is None:
            return self.initial_inventory
        return Inventory.parse_raw(inventory_json)

    async def write_inventory(self, inventory: Inventory):
        await self.client.set('atm_inventory', inventory.json())

    async def restart(self):
        await self.write_inventory(self.initial_inventory)

    async def acquire_lock(self):
        while True:
            if await self.client.setnx(self.lock_name, self.lock_value):
                await self.client.expire(self.lock_name, self.lock_timeout)
                return True
            elif await self.client.ttl(self.lock_name) == -1:
                await self.client.expire(self.lock_name, self.lock_timeout)
            await asyncio.sleep(0.001)  # Reduced sleep time to speed up retries

    async def release_lock(self):
        if await self.client.get(self.lock_name) == self.lock_value:
            await self.client.delete(self.lock_name)