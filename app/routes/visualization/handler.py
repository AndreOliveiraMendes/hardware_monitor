def get_level(score):
    if score >= 50:
        return 'critical'
    elif score >= 30:
        return 'high'
    elif score >= 15:
        return 'warning'
    return 'ok'