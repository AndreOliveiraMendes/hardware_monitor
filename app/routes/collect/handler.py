from flask import current_app

from app.dao import get_heat_score, insert_metric, update_heat_score
from app.notifier.notifier import send_mail, send_telegram

LEVEL_ORDER = {
    "ok": 0,
    "warning": 1,
    "high": 2,
    "critical": 3,
    "no temp": -1
}

def update_score(host_ip, device_type, name, temp):
    rows = get_heat_score(host_ip, device_type, name)
    if len(rows) > 1:
        score, level = 0, "imve"
    elif len(rows) == 0:
        score, level = 0, "???"
    else:
        score, level = rows[0]
        
    try:
        if device_type == 'CPU':
            if temp < 35:
                score = max(0, score - 7)
            elif temp < 50:
                score = max(0, score - 5)
            elif temp < 60:
                score = max(0, score - 3)
            elif temp < 70:
                score = max(0, score - 2)
            elif temp < 75:
                score += 1
            elif temp < 80:
                score += 2
            elif temp < 90:
                score += 3
            else:
                score += 5
        else:
            if temp < 35:
                score = max(0, score - 2)
            elif temp < 40:
                score = max(0, score - 1)
            elif temp < 45:
                score += 1
            elif temp < 50:
                score += 2
            elif temp < 55:
                score += 3
            else:
                score += 5

        if score >= 50:
            new_level = 'critical'
        elif score >= 30:
            new_level = 'high'
        elif score >= 15:
            new_level = 'warning'
        else:
            new_level = 'ok'
    except (ValueError, TypeError):
        score, new_level = -1, 'no temp'
        
    if new_level != level:
        old_rank = LEVEL_ORDER.get(level, -1)
        new_rank = LEVEL_ORDER.get(new_level, -1)

        if new_rank > old_rank:
            direction = "subiu"
        else:
            direction = "desceu"

        msg = f"level {direction} de {level} para {new_level}"
        if old_rank > 1:
            send_mail('ao_mendes@hotmail.com', new_level, msg)
        send_telegram(msg)
    
    return score, new_level

def collect_data(item):
    if item.get("source") == "remote" and item.get("target") is None:
        return 400, "target is required for remote source"

    # 1. Inserção (crítica)
    try:
        insert_metric(**item)
    except Exception as e:
        current_app.logger.warning(f"erro ao atualizar metrica:{e}")
        return 500, str(e)

    # 2. Update de estado (não crítico)
    try:
        if item.get("type") == "temperature":
            host_ip, device_type, name, value = item.get("host_ip"), item.get("device_type"), item.get("name"), item.get("value")
            score, level = update_score(host_ip, device_type, name, value)
            update_heat_score(host_ip, device_type, name, score, level)
    except Exception as e:
        # loga, mas NÃO quebra ingest
        current_app.logger.warning(f"erro ao atualizar o heat score:{e}")

    return 200, "Data inserted successfully"
