from typing import Any
import flet as ft
from flet.controls.material.navigation_drawer import NavigationDrawer


class AppDrawer(ft.NavigationDrawer):
    def __init__(self, page: ft.Page, on_nav_change=None):
        super().__init__()

        self._page = page
        self.on_nav_change = on_nav_change

        self.bgcolor = ft.Colors.BLACK
        self.elevation = 16

        self.controls = [
            # ft.Container(
            #     content=ft.Column(
            #         [
            #             ft.Icon(
            #                 ft.Icons.ACCOUNT_CIRCLE, size=40, color=ft.Colors.WHITE
            #             ),
            #             ft.Text(
            #                 "HERMES",
            #                 size=20,
            #                 weight=ft.FontWeight.BOLD,
            #                 color=ft.Colors.WHITE,
            #             ),
            #             ft.Text(
            #                 "seridi.mohammed.bachir@gmail.com",
            #                 size=12,
            #                 weight=ft.FontWeight.BOLD,
            #                 color=ft.Colors.BLACK,
            #             ),
            #         ]
            #     ),
            #     bgcolor=ft.Colors.BLUE_400,
            #     padding=ft.padding.all(20),
            #     width=float("inf"),
            # ),
            ft.Container(
                content=ft.Row(
                    [
                        ft.Icon(
                            ft.Icons.ACCOUNT_CIRCLE, size=40, color=ft.Colors.WHITE
                        ),
                        ft.Icon(ft.Icons.CR),
                    ]
                )
            ),
            ft.Divider(height=1, color=ft.Colors.BLUE_700),
            self._drawer_item(ft.Icons.HOME_ROUNDED, "Home", "home"),
            self._drawer_item(ft.Icons.INFO_ROUNDED, "About", "about"),
            self._drawer_item(ft.Icons.MAIL_ROUNDED, "Contact", "contact"),
            ft.Divider(height=3, color=ft.Colors.BLUE_GREY_700),
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
            padding=ft.Padding.symmetric(horizontal=20, vertical=14),
            ink=True,
            on_click=lambda e, r=route: self._handle_click(r),
            on_hover=self._on_hover,
        )

    async def _handle_click(self, route: str):
        await self._page.close_drawer()
        if self.on_nav_change:
            self.on_nav_change(route)

    def _on_hover(self, e):
        e.control.bgcolor = ft.Colors.BLUE_GREY_400 if e.data == "True" else None
        e.control.update()
