from flask import (Blueprint, current_app, jsonify, render_template, request,
                   url_for)

from app.dao import (get_all_heat_scores, get_filters, get_heat_score,
                     get_latest_metrics, get_metrics, get_temperature_series)

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route("/")
def menu():
    info = {
        "name": "Monitor API",
        "version": "1.0",
        "endpoints": [
            {
                "path": url_for('api.last_metrics'),
                "method": "GET",
                "description": "Get latest metrics"
            },
            {
                "path": url_for('api.all_metrics'),
                "method": "GET",
                "description": "Get all metrics according to the applied filters",
                "params": [
                    {
                        "name": "start",
                        "type": "datetime",
                        "required": False,
                        "example": "2026-04-18T00:00"
                    },
                    {
                        "name": "end",
                        "type": "datetime",
                        "required": False,
                        "example": "2026-04-18T23:59"
                    },
                    {
                        "name": "info_type",
                        "type": "string",
                        "required": False,
                        "example": "temperature"        
                    },
                    {
                        "name": "host_ip",
                        "type": "string",
                        "required": False,
                        "example": "17.70.13.0"  
                    },
                    {
                        "name": "device_type",
                        "type": "string",
                        "required": False,
                        "example": "CPU"
                    },
                    {
                        "name": "name",
                        "type": "string",
                        "required": False,
                        "example": "Core 0"
                    },
                    {
                        "name": "page",
                        "type": "integer",
                        "required": False,
                        "example": 0
                    }
                ]
            },
            {
                "path": url_for('api.filters'),
                "method": "GET",
                "description": "get relevant filters for info_type, device_type and name",
                "params": [
                    {
                        "name": "info_type",
                        "type": "string",
                        "required": False,
                        "example": "temperature"
                    },
                    {
                        "name": "host_ip",
                        "type": "string",
                        "required": False,
                        "example": "17.70.13.0"  
                    },
                    {
                        "name": "device_type",
                        "type": "string",
                        "required": False,
                        "example": "CPU"
                    }
                ]
            },
            {
                "path": url_for('api.get_hscore'),
                "method": "GET",
                "description": "get the heat score",
                "params":[
                    {
                        "name": "host_ip",
                        "type": "string",
                        "required": True,
                        "example": "192.168.5.50"
                    },
                    {
                        "name": "device_type",
                        "type": "string",
                        "required": True,
                        "example": "CPU"
                    },
                    {
                        "name": "name",
                        "type": "string",
                        "required": True,
                        "example": "Core 0"
                    }
                ]
            },
            {
                "path": url_for('api.get_ahscore'),
                "method": "GET",
                "description": "get all the heat score",
                "params":[
                ]
            },
            {
                "path": url_for('api.temperature_series'),
                "method": "GET",
                "description": "obtem a series de dados de temperatura",
                "params": [
                    {
                        "name": "start",
                        "type": "datetime",
                        "required": False,
                        "example": "2026-04-18T00:00"
                    },
                    {
                        "name": "end",
                        "type": "datetime",
                        "required": False,
                        "example": "2026-04-18T23:59"
                    },
                    {
                        "name": "host_ip",
                        "type": "string",
                        "required": False,
                        "example": "17.70.13.0"  
                    },
                    {
                        "name": "device_type",
                        "type": "string",
                        "required": False,
                        "example": "CPU"
                    },
                    {
                        "name": "name",
                        "type": "string",
                        "required": False,
                        "example": "Core 0"
                    },
                    {
                        "name": "page",
                        "type": "integer",
                        "required": False,
                        "example": 0
                    }
                ]
            }
        ]
    }

    if "application/json" in request.headers.get("Accept", ""):
        return jsonify(info)
    else:
        return render_template("api/menu.html", info=info)

@bp.route("/latest")
def last_metrics():
    return jsonify(get_latest_metrics())

@bp.route("/metrics")
def all_metrics():
    try:
        page = int(request.args.get("page", 0))
    except (ValueError, TypeError):
        page = 0

    start = request.args.get("start")
    end = request.args.get("end")
    host_ip = request.args.get("host_ip")
    tipo_informacao = request.args.get("info_type")
    tipo_dispositivo = request.args.get("device_type")
    name = request.args.get("name")

    result = get_metrics(start, end, host_ip, tipo_informacao, tipo_dispositivo, name, page)

    data = []
    for row in result["data"]:
        data.append({
            "timestamp": row[0],
            "hostname": row[1],
            "host_ip": row[2],
            "infotype": row[3],
            "device_type": row[4],
            "name": row[5],
            "value": row[6],
            "meta": row[7]
        })

    return jsonify({
        "data": data,
        "page": result["page"],
        "per_page": result["per_page"],
        "total": result["total"],
        "has_next": result["has_next"],
        "has_prev": result["has_prev"]
    })

@bp.route("/filters")
def filters():
    info_type = request.args.get("info_type")
    host_ip = request.args.get("host_ip")
    device_type = request.args.get("device_type")

    info_types, host_ips, device_types, names = get_filters(info_type, host_ip, device_type)

    return jsonify({
        "info_types": info_types,
        "host_ips": host_ips,
        "device_types": device_types,
        "names": names
    })

@bp.route("/heat_score")
def get_hscore():
    host_ip = request.args.get("host_ip")
    device_type = request.args.get("device_type")
    name = request.args.get("name")
    
    if not host_ip or not device_type or not name:
        current_app.logger.error(f"not enought info: ({host_ip}, {device_type}, {name})")
        return jsonify({"error": "not enought information"}), 500
    
    return jsonify(get_heat_score(host_ip, device_type, name))

@bp.route("/all_heat_score")
def get_ahscore():
    return jsonify(get_all_heat_scores())

@bp.route("/temperature-series")
def temperature_series():
    host_ip = request.args.get("host_ip")
    device_type = request.args.get("device_type")
    name = request.args.get("name")
    start = request.args.get("start")
    end = request.args.get("end")

    try:
        page = int(request.args.get("page", 0))
    except:
        page = 0

    rows = get_temperature_series(host_ip, device_type, name, start, end, page)

    # transforma em dict (melhor pro frontend)
    data = [
        {
            "timestamp": r[0],
            "hostname": r[1],
            "host_ip": r[2],
            "device_type": r[3],
            "name": r[4],
            "value": r[5],
        }
        for r in rows
    ]

    return jsonify(data)
