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