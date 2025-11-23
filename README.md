# fingal-fleet
Local-first Tesla Powerwall fleet controller, sub-second dispatch, DS3 FFR ready 

fingal-fleet v0.8.0Local-first, open-source Tesla Powerwall fleet controller![License: MIT]
green.svg) (LICENSE)
Python
FastAPINo cloud required. Sub-second control. Built for the community.bash

docker compose up --build
# → http://localhost:8000/v2g

What it isfingal-fleet is a minimal, fully open-source controller for one or many Tesla Powerwalls (and future bidirectional vehicles).
It speaks directly to the local Gateway API, giving you the fastest possible response time and complete independence from Tesla’s cloud.Originally started as a idea has grown into a clean, observable, and extensible platform that anyone can run, study, or improve.Core principlesLocal-first – works during internet outages  
Deterministic metrics – byte-exact change detection (zero metric churn)  
Native OpenTelemetry + Prometheus – drop-in Grafana/Prometheus ready  
Single-file SQLite persistence – no external database  
Security by design – optional API key + TOTP 2FA + mTLS + IP allow-list  
MIT licensed – use it anywhere, modify it freely

Who this is forHome Assistant users wanting rock-solid Powerwall integration  
Researchers studying battery behaviour and grid interaction  
Renewable energy cooperatives running small fleets  
Developers who value clean, well-documented Python code  
Anyone who prefers local control over cloud dependency

FeaturesFeature
Status
Notes
Sub-second local dispatch
Done
Direct Gateway API
DS3 FFR-ready (<750 ms reaction)
Done
Local control only
Deterministic change detection
Done
orjson + OPT_SORT_KEYS
Live Streamlit dashboard
Done
Real-time fleet view
Nuclear-grade auth (optional)
Done
2FA + mTLS + IP filtering
OpenTelemetry + Prometheus
Done
Production observability
100 % pytest coverage (critical paths)
Done
Verified locally

Quick startbash

git clone https://github.com/danielhfingal/fingal-fleet.git
cd fingal-fleet
cp .env.example .env
# Edit sites.yaml and .env
docker compose up --build

/v2g → Live Streamlit dashboard  
/metrics → Prometheus endpoint  
/healthz → Health check

Contributing
Every line in this project has a reason to exist.
Its in the hands of the people now...

LicenseMIT License — free for personal, research, and commercial use.AuthorDaniel H. Fingal
Portugal · 2025  “All carpet fringes perfectly aligned.”
fingal-fleet — open source, local-first.
The Energy belongs to everyone.

