import flet as ft


class AppDrawer(ft.NavigationDrawer):
    def __init__(self, page: ft.Page, on_nav_change=None):
        super().__init__()

        self.on_nav_change = on_nav_change

        # Drawer styling
        self.bgcolor = ft.Colors.BLUE_GREY_900
        self.elevation = 16

        self.controls = [
            # Header section
            ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(
                            ft.Icons.ACCOUNT_CIRCLE, size=60, color=ft.Colors.WHITE
                        ),
                        ft.Text(
                            "MyApp",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE,
                        ),
                        ft.Text(
                            "myapp@email.com", size=12, color=ft.Colors.BLUE_GREY_200
                        ),
                    ]
                ),
                bgcolor=ft.Colors.BLUE_700,
                padding=ft.padding.all(20),
                width=float("inf"),
            ),
            ft.Divider(height=1, color=ft.Colors.BLUE_GREY_700),
            # Nav items
            self._drawer_item(ft.Icons.HOME_ROUNDED, "Home", "home"),
            self._drawer_item(ft.Icons.INFO_ROUNDED, "About", "about"),
            self._drawer_item(ft.Icons.MAIL_ROUNDED, "Contact", "contact"),
            ft.Divider(height=1, color=ft.Colors.BLUE_GREY_700),
            self._drawer_item(ft.Icons.SETTINGS_ROUNDED, "Settings", "settings"),
            self._drawer_item(ft.Icons.LOGOUT_ROUNDED, "Logout", "logout"),
        ]

    def _drawer_item(self, icon, label: str, route: str) -> ft.Container:
        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(icon, color=ft.Colors.WHITE, size=20),
                    ft.Text(label, color=ft.Colors.WHITE, size=15),
                ],
                spacing=16,
            ),
            padding=ft.padding.symmetric(horizontal=20, vertical=14),
            border_radius=8,
            ink=True,  # ripple effect on click
            on_click=lambda e, r=route: self._handle_click(r),
            on_hover=self._on_hover,
        )

    def _on_hover(self, e):
        e.control.bgcolor = ft.Colors.BLUE_GREY_700 if e.data == "true" else None
        e.control.update()

    async def _handle_click(self, route: str):
        await ft.Page.window.close()  # close drawer after selection
        if self.on_nav_change:
            self.on_nav_change(route)

