import asyncio
import time
import orjson
from datetime import datetime, UTC
from pypowerwall import Powerwall
from tenacity import retry, stop_after_attempt, wait_exponential
from .database import SessionLocal, Site
from .dispatch import Dispatcher

class FleetPowerwall:
    def __init__(self, site_id: str, cfg: dict):
        self.site_id = site_id
        self.cfg = cfg
        self.labels = cfg.get("labels", {})
        self._last_state_bytes = None
        self.pw = Powerwall(
            host=cfg.get("host"),
            password=cfg.get("password", ""),
            email=cfg.get("email", ""),
            cloudmode=bool(cfg.get("fleet_api")),
            siteid=cfg.get("site_id"),
        )
        self.dispatcher = Dispatcher(self.pw)

    @retry(stop=stop_after_attempt(12), wait=wait_exponential(multiplier=2, max=120))
    async def poll(self):
        state = await asyncio.to_thread(self.pw.soestatus)
        vitals = await asyncio.to_thread(self.pw.vitals)
        state["vitals"] = vitals

        state_bytes = orjson.dumps(state, option=orjson.OPT_SORT_KEYS)
        changed = state_bytes != self._last_state_bytes
        self._last_state_bytes = state_bytes

        db = SessionLocal()
        db.query(Site).filter(Site.id == self.site_id).update({
            "last_seen": datetime.now(UTC),
            "current_soc": state.get("battery_soe", 0),
            "current_power_kw": state.get("site_power", 0),
        })
        db.commit()
        db.close()

        return {"site_id": self.site_id, "changed": changed, "state": state}