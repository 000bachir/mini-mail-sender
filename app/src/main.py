import flet as ft

from app.Mailer.sender import EMAIL, EmailManager, EmailSender
from app.src.components.navigationBar import navigationBar

# ── Design Tokens ─────────────────────────────────────────────────────────────
SURFACE = "#050f1c"
SURFACE_LOW = "#041426"
SURFACE_HIGH = "#00274a"
SURFACE_CONTAINER = "#031a33"
PRIMARY = "#adc6ff"
PRIMARY_CONT = "#004395"
SECONDARY = "#06b77f"
SEC_CONTAINER = "#0a2e22"
ERR_CONTAINER = "#3b1212"
ON_SURFACE = "#d8e6ff"
ON_SURFACE_VAR = "#8daddb"
OUTLINE_VAR = "#274971"
WARN = "#f5a623"
ERROR = "#ff6b6b"


# ── Helpers ───────────────────────────────────────────────────────────────────
def with_opacity(color: str, opacity: float) -> str:
    color = color.lstrip("#")
    r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
    return f"rgba({r},{g},{b},{opacity})"


def label_sm(text, color=ON_SURFACE_VAR):
    return ft.Text(
        text.upper(),
        size=9,
        color=color,
        weight=ft.FontWeight.W_500,
        style=ft.TextStyle(letter_spacing=1.2),
    )


def display_lg(text, size=48, color=ON_SURFACE):
    return ft.Text(text, size=size, color=color, weight=ft.FontWeight.W_300)


def mono(text, size=11, color=ON_SURFACE_VAR):
    return ft.Text(text, size=size, color=color, font_family="monospace")


# ── Chip / Badge ──────────────────────────────────────────────────────────────
def chip(text, bg, fg):
    return ft.Container(
        content=ft.Text(
            text.upper(),
            size=9,
            color=fg,
            weight=ft.FontWeight.W_500,
            style=ft.TextStyle(letter_spacing=0.8),
        ),
        bgcolor=bg,
        border_radius=2,
        padding=ft.padding.symmetric(horizontal=10, vertical=3),
    )


# ── Log Entry ─────────────────────────────────────────────────────────────────
def log_entry(time, level, message, idx=0):
    color = {"OK": SECONDARY, "WRN": WARN, "ERR": ERROR}.get(level, ON_SURFACE_VAR)
    bg = SURFACE_LOW if idx % 2 == 0 else "#040f1e"
    return ft.Container(
        content=ft.Row(
            [
                mono(time, color="#4a6a8a"),
                mono(level, color=color),
                mono(message),
            ],
            spacing=12,
        ),
        bgcolor=bg,
        padding=ft.padding.symmetric(horizontal=6, vertical=3),
    )


def main(page: ft.Page):
    page.add(ft.Text("Hello wrold from whe"), navigationBar("test", "text"))
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.AMBER)


ft.app(target=main)
