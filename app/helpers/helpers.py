from datetime import datetime

from flask import Flask


def templater_helpers(app:Flask):
    @app.template_filter('dia')
    def format_dia(value):
        return value.strftime("%d/%m/%Y")
    
    @app.template_filter('hora')
    def format_hora(value):
        return value.strftime("%H:%M:%S")
    
    @app.template_filter('datahora')
    def format_datahora(value):
        return datetime.fromisoformat(value).strftime("%d/%m/%Y %H:%M:%S")
    
    @app.template_filter('input_type')
    def input_type(it):
        if it in ["integer", "number", "float"]:
            return "number"
        elif it == "boolean":
            return "checkbox"
        elif it in ["password", "email", "date", "time"]:
            return it
        elif it == "datetime":
            return "datetime-local"
        elif it in ["string", "text"]:
            return "text"
        elif it in ["url", "uri"]:
            return "url"
        elif it == "file":
            return "file"
        elif it in ["json", "object", "array", "uuid"]:
            return "text"
        elif it == "enum":
            return "select"
        return "text"