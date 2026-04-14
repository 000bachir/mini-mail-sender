import flet as ft


class SideBar(ft.Container):
    def __init__(self) -> None:
        super().__init__()

        self.content = ft.Column(
            controls=[
                ft.Text("sidebar"),
                ft.ElevatedButton("home"),
                ft.ElevatedButton("settings"),
            ]
        )

