# fingal_fleet/main.py — v0.8.0 — The grid is ours
from __future__ import annotations
import asyncio
import logging
import yaml
from datetime import datetime, UTC
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from opentelemetry import metrics
from opentelemetry.exporter.prometheus import PrometheusMetricsExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
from .database import SessionLocal, Site
from .site import FleetPowerwall
from .dispatch import Cmd
from .hardened_security import Nuclear

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger("fingal-fleet")

app = FastAPI(title="fingal-fleet v0.8.0 — The Money Printer", version="0.8.0")

resource = Resource.create({"service.name": "fingal-fleet", "version": "0.8.0"})
metrics.set_meter_provider(MeterProvider(resource=resource))
meter = metrics.get_meter("fingal-fleet")
exporter = PrometheusMetricsExporter()
metrics.get_meter_provider().start_pipeline(exporter.reader)
app.mount("/metrics", exporter.create_app())

FLEET_SITE_UP = meter.create_up_down_counter("fleet_site_up", description="1 = site alive")
FLEET_COMMAND_TOTAL = meter.create_counter("fleet_command_total", description="Commands issued")

sites: dict[str, FleetPowerwall] = {}
command_queue: asyncio.Queue[tuple[str, Cmd]] = asyncio.Queue()

def load_sites():
    path = Path("sites.yaml")
    if not path.exists(): raise FileNotFoundError("sites.yaml")
    config = yaml.safe_load(path.read_text())
    for site_cfg in config.get("sites", []):
        sid = site_cfg["id"]
        sites[sid] = FleetPowerwall(sid, site_cfg)
        db = SessionLocal()
        db.merge(Site(id=sid, config=site_cfg, labels=site_cfg.get("labels", {}), is_active=True))
        db.commit()
        db.close()
    log.info(f"Fleet loaded — {len(sites)} Powerwall(s) armed")

load_sites()

async def command_worker():
    while True:
        site_id, cmd = await command_queue.get()
        targets = [sites[site_id]] if site_id != "all" else sites.values()
        for target in targets:
            await target.dispatcher.run(cmd)
            FLEET_COMMAND_TOTAL.add(1, {"site_id": target.site_id, "cmd": cmd.value})

async def poll_loop(site_id: str):
    pw = sites[site_id]
    while True:
        try:
            result = await pw.poll()
            if result["changed"]: pass
            FLEET_SITE_UP.add(1, {"site_id": site_id})
        except Exception: FLEET_SITE_UP.add(-1, {"site_id": site_id})
        await asyncio.sleep(8 + (asyncio.get_running_loop().time() % 3))

@app.on_event("startup")
async def startup():
    log.info("fingal-fleet v0.8.0 — The fleet awakens")
    asyncio.create_task(command_worker())
    for sid in sites: asyncio.create_task(poll_loop(sid))

@app.get("/healthz") 
async def healthz(): return {"status": "ok", "sites": len(sites)}

@app.get("/", response_class=HTMLResponse)
async def root(_: Request):
    db = SessionLocal(); count = db.query(Site).count(); db.close()
    return HTMLResponse(f"<h1>fingal-fleet v0.8.0</h1><p>{count} Powerwalls • <a href=/v2g>Dashboard</a> • <a href=/metrics>Metrics</a></p>")

@app.post("/dispatch/{cmd}", dependencies=[Nuclear])
async def dispatch_fleet(cmd: Cmd):
    for sid in sites: await command_queue.put((sid, cmd))
    return {"status": "PRINTING", "sites": len(sites)}

@app.post("/dispatch/discharge", dependencies=[Nuclear])
@app.post("/dispatch/charge", dependencies=[Nuclear])
@app.post("/dispatch/ffr", dependencies=[Nuclear])
async def quick_dispatch(cmd: str):
    valid = {"discharge": Cmd.DISCHARGE, "charge": Cmd.CHARGE, "ffr": Cmd.FFR}
    await command_queue.put(("all", valid[cmd]))
    return {"status": "PRINTING", "cmd": cmd}