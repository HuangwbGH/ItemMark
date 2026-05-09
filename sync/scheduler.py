import time
from datetime import datetime, timedelta

from module_config import list_module_configs
from sync_runner import run_sync


last_interval_runs = {}


def _cron_due(cron_expr: str, now: datetime) -> bool:
    parts = cron_expr.split()
    if len(parts) != 5:
        return False
    minute_expr, hour_expr = parts[0], parts[1]
    minutes = {int(minute_expr)} if minute_expr.isdigit() else set()
    hours = {int(h) for h in hour_expr.split(",") if h.isdigit()}
    return now.minute in minutes and now.hour in hours


def _interval_due(module_key: str, minutes: int, now: datetime) -> bool:
    last = last_interval_runs.get(module_key)
    if not last or now - last >= timedelta(minutes=minutes):
        last_interval_runs[module_key] = now
        return True
    return False


def main() -> None:
    while True:
        now = datetime.now().replace(second=0, microsecond=0)
        for cfg in list_module_configs():
            if not cfg.sync_enabled:
                continue
            due = False
            if cfg.sync_mode == "interval":
                due = _interval_due(cfg.module_key, cfg.interval_minutes, now)
            else:
                due = _cron_due(cfg.sync_cron, now)
            if due:
                run_sync(cfg.module_key, "auto", "incremental")
        time.sleep(60)


if __name__ == "__main__":
    main()
