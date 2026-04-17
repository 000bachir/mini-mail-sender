import flet as ft
from starlette.responses import Content


class Navbar(ft.Container):
    def __init__(self, page: ft.Page, on_nav_change=None, on_drawer_open=None):
        super().__init__()

        self.on_nav_change = on_nav_change
        self.on_drawer_open = on_drawer_open  # NEW

        self.bgcolor = ft.Colors.BLUE_700
        self.padding = ft.padding.symmetric(horizontal=20, vertical=10)
        self.width = float("inf")

        self.content = ft.Row(
            controls=[
                # Hamburger button — triggers drawer
                ft.IconButton(
                    icon=ft.Icons.MENU_ROUNDED,
                    icon_color=ft.Colors.WHITE,
                    tooltip="Open menu",
                    on_click=lambda e: self._open_drawer(),
                ),
                # Brand
                ft.Text(
                    "MyApp",
                    size=22,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE,
                ),
                ft.Container(expand=True),
                # Nav links (visible on wider screens)
                self._nav_button("Home", "home"),
                self._nav_button("About", "about"),
                self._nav_button("Contact", "contact"),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def _nav_button(self, label: str, route: str) -> ft.TextButton:
        return ft.TextButton(
            content=label,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                overlay_color=ft.Colors.BLUE_500,
            ),
            on_click=lambda e, r=route: self._handle_click(r),
        )

    def _handle_click(self, route: str):
        if self.on_nav_change:
            self.on_nav_change(route)

    def _open_drawer(self):
        if self.on_drawer_open:
            self.on_drawer_open()
