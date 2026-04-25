from datetime import datetime

from flask import Blueprint, jsonify, render_template, request, url_for

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
    tipo_info = request.args.get("info_type")
    tipo_temp = request.args.get("device_type")
    name = request.args.get("name")
    
    rows = get_metrics(start, end, tipo_info, tipo_temp, name, page)

    data = []
    for row in rows:
        data.append({
            "timestamp": row[0],
            "infotype": row[1],
            "device_type": row[2],
            "name": row[3],
            "value": row[4],
            "meta": row[5]
        })

    return jsonify(data)

@bp.route("/filters")
def filters():
    info_type = request.args.get("info_type")
    device_type = request.args.get("device_type")

    info_types, device_types, names = get_filters(info_type, device_type)

    return jsonify({
        "info_types": info_types,
        "device_types": device_types,
        "names": names
    })

@bp.route("/heat_score")
def get_hscore():
    host_ip = request.args.get("host_ip")
    device_type = request.args.get("device_type")
    name = request.args.get("name")
    
    if not host_ip or device_type or name:
        return jsonify({"error": "not enought information"}), 500
    
    return jsonify(get_heat_score(host_ip, device_type, name))

@bp.route("/all_heat_score")
def get_ahscore():
    return jsonify(get_all_heat_scores())

@bp.route("/temperature-series")
def temperature_series():
    device_type = request.args.get("device_type")
    name = request.args.get("name")
    start = request.args.get("start")
    end = request.args.get("end")

    try:
        page = int(request.args.get("page", 0))
    except:
        page = 0

    rows = get_temperature_series(device_type, name, start, end, page)

    # transforma em dict (melhor pro frontend)
    data = [
        {
            "timestamp": r[0],
            "device_type": r[1],
            "name": r[2],
            "value": r[3],
        }
        for r in rows
    ]

    return jsonify(data)