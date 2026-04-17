import flet as ft
from app.src.components.navigationBar import Navbar
from app.src.components.sidebar import AppDrawer


def main(page: ft.Page):
    page.title = "Hermes"
    page.padding = 0

    content_area = ft.Container(
        content=ft.Text("Welcome to Home!", size=24),
        padding=40,
        expand=True,
    )

    def on_nav_change(route: str):
        """Shared handler — used by both Navbar and Drawer."""
        pages = {
            "home": ft.Text("Welcome to Home!", size=24),
            "about": ft.Text("About Us page.", size=24),
            "contact": ft.Text("Contact page.", size=24),
            "settings": ft.Text("Settings page.", size=24),
            "logout": ft.Text("Logged out.", size=24),
        }
        content_area.content = pages.get(route, ft.Text("Page not found"))
        page.update()

    def open_drawer(e=None):
        if page.drawer:
            page.drawer.open = True
            page.update()

    # Build components
    drawer = AppDrawer(page=page, on_nav_change=on_nav_change)
    navbar = Navbar(page=page, on_nav_change=on_nav_change, on_drawer_open=open_drawer)

    # Register drawer on the page
    page.drawer = drawer

    page.add(
        ft.Column(
            controls=[
                navbar,
                content_area,
            ],
            expand=True,
            spacing=0,
        )
    )


ft.app(target=main)
