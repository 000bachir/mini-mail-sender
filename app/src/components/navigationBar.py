from fastapi.routing import request_response
import flet as fl


def navigationBar(label, value):
    return fl.Container(content=fl.Column([fl.Text(label), fl.Text(value)]))
