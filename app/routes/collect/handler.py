from app.db import insert_metric


def collect_data(item):
    if item.get("source") == "remote" and item.get("target") is None:
        return 400, "target is required for remote source"
    try:
        insert_metric(**item)
        return 200, "Data inserted successfully"
    except Exception as e:
        return 500, str(e)
