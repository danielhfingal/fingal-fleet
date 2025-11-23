from __future__ import annotations
import asyncio
from enum import StrEnum
from pypowerwall import Powerwall

class Cmd(StrEnum):
    DISCHARGE = "discharge"
    CHARGE = "charge"
    FFR = "ffr"

class Dispatcher:
    def __init__(self, pw: Powerwall):
        self.pw = pw

    async def _force(self):
        await asyncio.to_thread(self.pw.set_operation, "self_consumption")
        try: await asyncio.to_thread(self.pw.set_storm_mode, False)
        except: pass

    async def discharge(self): await self._force(); await asyncio.to_thread(self.pw.set_backup_reserve_percent, 0)
    async def charge(self):    await self._force(); await asyncio.to_thread(self.pw.set_backup_reserve_percent, 100)
    async def ffr(self):       await self._force(); await asyncio.to_thread(self.pw.set_backup_reserve_percent, 0)

    async def run(self, cmd: Cmd):
        {"discharge": self.discharge, "charge": self.charge, "ffr": self.ffr}[cmd]()