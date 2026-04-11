import flet as ft

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


# ── Telemetry Card ────────────────────────────────────────────────────────────
def telemetry_card(label, value, value_color=ON_SURFACE, sparkline_color=PRIMARY):
    pts = {
        PRIMARY: [(0, 28), (13, 22), (26, 25), (39, 10), (52, 16), (65, 8), (80, 4)],
        WARN: [(0, 10), (13, 18), (26, 12), (39, 20), (52, 14), (65, 22), (80, 16)],
        SECONDARY: [(0, 16), (13, 14), (26, 16), (39, 12), (52, 14), (65, 10), (80, 8)],
    }.get(sparkline_color, [(0, 20), (40, 10), (80, 5)])

    shapes = [
        ft.canvas.Path(
            [ft.canvas.Path.MoveTo(pts[0][0], pts[0][1])]
            + [ft.canvas.Path.LineTo(x, y) for x, y in pts[1:]],
            paint=ft.Paint(
                stroke_width=1.5, style=ft.PaintingStyle.STROKE, color=sparkline_color
            ),
        )
    ]
    return ft.Container(
        content=ft.Stack(
            [
                ft.Column(
                    [
                        label_sm(label),
                        ft.Container(height=6),
                        ft.Text(
                            value,
                            size=28,
                            color=value_color,
                            weight=ft.FontWeight.W_300,
                        ),
                    ]
                ),
                ft.Container(
                    content=ft.canvas.Canvas(shapes=shapes, width=80, height=36),
                    right=0,
                    bottom=0,
                    opacity=0.35,
                ),
            ]
        ),
        bgcolor=SURFACE_LOW,
        padding=20,
        expand=True,
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


# ── Buttons ───────────────────────────────────────────────────────────────────
def btn_primary(text, on_click=None):
    return ft.ElevatedButton(
        text=text.upper(),
        color=SURFACE,
        bgcolor=PRIMARY_CONT,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=2),
            text_style=ft.TextStyle(
                size=11, letter_spacing=1.2, weight=ft.FontWeight.W_500
            ),
            padding=ft.padding.symmetric(horizontal=18, vertical=8),
        ),
        on_click=on_click,
    )


def btn_secondary(text, on_click=None):
    return ft.OutlinedButton(
        text=text.upper(),
        style=ft.ButtonStyle(
            color=ON_SURFACE,
            side=ft.BorderSide(1, OUTLINE_VAR),
            shape=ft.RoundedRectangleBorder(radius=2),
            text_style=ft.TextStyle(size=11, letter_spacing=1.2),
            padding=ft.padding.symmetric(horizontal=18, vertical=8),
        ),
        on_click=on_click,
    )


def btn_ghost(text, on_click=None):
    return ft.TextButton(
        text=text.upper(),
        style=ft.ButtonStyle(
            color=ON_SURFACE_VAR,
            shape=ft.RoundedRectangleBorder(radius=2),
            text_style=ft.TextStyle(size=11, letter_spacing=1.2),
            padding=ft.padding.symmetric(horizontal=18, vertical=8),
        ),
        on_click=on_click,
    )


# ── Field Input ───────────────────────────────────────────────────────────────
def field_input(label, value="", password=False):
    return ft.Column(
        [
            label_sm(label),
            ft.TextField(
                value=value,
                password=password,
                can_reveal_password=password,
                bgcolor=SURFACE_CONTAINER,
                border_color="transparent",
                focused_border_color=PRIMARY,
                border_width=0,
                focused_border_width=2,
                border_radius=ft.border_radius.only(top_left=2, top_right=2),
                color=ON_SURFACE,
                cursor_color=SECONDARY,
                text_size=12,
                content_padding=ft.padding.symmetric(horizontal=12, vertical=8),
            ),
        ],
        spacing=6,
    )


# ── Nav Item ──────────────────────────────────────────────────────────────────
def nav_item(_, text, route, current_route, page):
    active = current_route == route
    color = PRIMARY if active else ON_SURFACE_VAR

    def go(e):
        page.push_route(route)

    return ft.Container(
        content=ft.Row(
            [
                ft.Text("◆" if active else "◇", size=10, color=color),
                ft.Text(
                    text, size=12, color=color, style=ft.TextStyle(letter_spacing=0.4)
                ),
            ],
            spacing=8,
        ),
        padding=ft.padding.symmetric(horizontal=20, vertical=8),
        bgcolor=with_opacity(PRIMARY, 0.05) if active else "transparent",
        border=ft.border.only(
            left=ft.BorderSide(2, PRIMARY if active else "transparent")
        ),
        on_click=go,
        ink=True,
    )


# ── Sidebar ───────────────────────────────────────────────────────────────────
def sidebar(current_route, page):
    nav_sections = [
        (
            "workspace",
            [
                ("dashboard", "Dashboard", "/dashboard"),
                ("telemetry", "Telemetry", "/telemetry"),
                ("automation", "Automation", "/automation"),
            ],
        ),
        (
            "system",
            [
                ("terminal", "Terminal", "/terminal"),
                ("activity", "Activity", "/activity"),
                ("settings", "Settings", "/settings"),
            ],
        ),
    ]

    items = [
        ft.Container(
            content=ft.Row(
                [
                    ft.Text("◈", size=14, color=PRIMARY),
                    ft.Text(
                        "PRECIS",
                        size=11,
                        color=ON_SURFACE_VAR,
                        weight=ft.FontWeight.W_500,
                        style=ft.TextStyle(letter_spacing=1.5),
                    ),
                ],
                spacing=6,
            ),
            padding=ft.padding.only(left=20, bottom=20),
        )
    ]

    for section_label, routes in nav_sections:
        items.append(
            ft.Container(
                content=ft.Text(
                    section_label.upper(),
                    size=9,
                    color=with_opacity(ON_SURFACE_VAR, 0.4),
                    style=ft.TextStyle(letter_spacing=1.5),
                ),
                padding=ft.padding.only(left=20, top=16, bottom=6),
            )
        )
        for _, label, route in routes:
            items.append(nav_item(None, label, route, current_route, page))

    return ft.Container(
        content=ft.Column(items, spacing=2),
        bgcolor=SURFACE_LOW,
        width=200,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Pages
# ─────────────────────────────────────────────────────────────────────────────


def dashboard_page(page):
    logs = [
        ("09:41:02", "OK", "pipeline.run completed"),
        ("09:40:55", "WRN", "memory threshold 78%"),
        ("09:40:48", "OK", "worker:3 spawned"),
        ("09:40:41", "OK", "task queue flushed"),
        ("09:40:33", "ERR", "conn timeout node:7"),
        ("09:40:27", "OK", "auth.refresh success"),
    ]
    return ft.Column(
        [
            ft.Column(
                [
                    label_sm("System Health"),
                    ft.Row(
                        [
                            display_lg("99.4%"),
                            ft.Container(
                                content=ft.Text("↑ nominal", size=13, color=SECONDARY),
                                margin=ft.margin.only(left=10, top=14),
                            ),
                        ]
                    ),
                ],
                spacing=6,
            ),
            ft.Container(height=24),
            ft.Row(
                [
                    telemetry_card("Requests / sec", "2,841", PRIMARY, PRIMARY),
                    telemetry_card("Avg Latency", "184ms", WARN, WARN),
                    telemetry_card("Success Rate", "99.8%", SECONDARY, SECONDARY),
                ],
                spacing=1,
            ),
            ft.Container(height=20),
            ft.Row(
                [
                    ft.Container(
                        content=ft.Column(
                            [
                                label_sm("Activity Log"),
                                ft.Container(height=8),
                                ft.Row(
                                    [
                                        chip("Running", SEC_CONTAINER, SECONDARY),
                                        chip(
                                            "3 Workers",
                                            with_opacity(PRIMARY, 0.1),
                                            PRIMARY,
                                        ),
                                        chip("1 Alert", with_opacity(WARN, 0.15), WARN),
                                    ],
                                    spacing=6,
                                ),
                                ft.Container(height=8),
                                ft.Column(
                                    [
                                        log_entry(t, l, m, i)
                                        for i, (t, l, m) in enumerate(logs)
                                    ],
                                    spacing=0,
                                ),
                            ]
                        ),
                        bgcolor=SURFACE_LOW,
                        padding=20,
                        expand=True,
                    ),
                    ft.Container(
                        content=ft.Column(
                            [
                                label_sm("Configuration"),
                                ft.Container(height=10),
                                ft.Container(
                                    content=ft.Text(
                                        "◈ GLASSMORPHIC ELEMENT",
                                        size=9,
                                        color=PRIMARY,
                                        style=ft.TextStyle(letter_spacing=0.8),
                                    ),
                                    bgcolor=with_opacity(SURFACE_HIGH, 0.7),
                                    border=ft.border.all(
                                        1, with_opacity(OUTLINE_VAR, 0.2)
                                    ),
                                    border_radius=2,
                                    padding=ft.padding.symmetric(
                                        horizontal=14, vertical=6
                                    ),
                                ),
                                ft.Container(height=10),
                                field_input("Endpoint", "https://api.precision.io/v2"),
                                ft.Container(height=10),
                                field_input(
                                    "Auth Token", "sk_live_••••••••", password=True
                                ),
                                ft.Container(height=10),
                                ft.Container(
                                    content=ft.Row(
                                        [
                                            ft.Text(
                                                "$",
                                                size=12,
                                                color=SECONDARY,
                                                font_family="monospace",
                                            ),
                                            ft.TextField(
                                                hint_text="run pipeline --env prod",
                                                hint_style=ft.TextStyle(
                                                    color=with_opacity(
                                                        ON_SURFACE_VAR, 0.3
                                                    )
                                                ),
                                                bgcolor="transparent",
                                                border_color="transparent",
                                                color=ON_SURFACE,
                                                cursor_color=SECONDARY,
                                                text_size=12,
                                                font_family="monospace",
                                                expand=True,
                                                content_padding=0,
                                            ),
                                        ],
                                        spacing=8,
                                    ),
                                    bgcolor=SURFACE_CONTAINER,
                                    padding=ft.padding.symmetric(
                                        horizontal=12, vertical=8
                                    ),
                                    border=ft.border.only(
                                        bottom=ft.BorderSide(2, PRIMARY)
                                    ),
                                ),
                                ft.Container(height=14),
                                ft.Row(
                                    [
                                        btn_primary("Deploy"),
                                        btn_secondary("Preview"),
                                        btn_ghost("Reset"),
                                    ],
                                    spacing=8,
                                ),
                            ]
                        ),
                        bgcolor=SURFACE_LOW,
                        padding=20,
                        expand=True,
                    ),
                ],
                spacing=20,
            ),
        ],
        spacing=0,
        scroll=ft.ScrollMode.AUTO,
    )


def telemetry_page(page):
    metrics = [
        ("CPU Usage", "67%", WARN, WARN),
        ("Memory", "4.2 GB", PRIMARY, PRIMARY),
        ("Disk I/O", "1.1 GB/s", SECONDARY, SECONDARY),
        ("Network Out", "340 MB/s", PRIMARY, PRIMARY),
        ("Error Rate", "0.02%", SECONDARY, SECONDARY),
        ("Queue Depth", "12", WARN, WARN),
    ]
    cards = [telemetry_card(l, v, vc, sc) for l, v, vc, sc in metrics]
    rows = [ft.Row(cards[i : i + 3], spacing=1) for i in range(0, len(cards), 3)]
    return ft.Column(
        [
            label_sm("Telemetry Overview"),
            ft.Container(height=4),
            display_lg("Live Metrics"),
            ft.Container(height=24),
            *rows,
        ],
        spacing=12,
        scroll=ft.ScrollMode.AUTO,
    )


def terminal_page(page):
    history = ft.Column([], spacing=0, scroll=ft.ScrollMode.AUTO)
    input_ref = ft.Ref[ft.TextField]()

    def run_cmd(e):
        cmd = input_ref.current.value.strip()
        if not cmd:
            return
        history.controls.append(
            ft.Container(
                content=ft.Row(
                    [mono("$", color=SECONDARY), mono(cmd, color=ON_SURFACE)], spacing=8
                ),
                padding=ft.padding.symmetric(vertical=2),
            )
        )
        history.controls.append(
            ft.Container(
                content=mono(f"→ executed: {cmd}", color=ON_SURFACE_VAR),
                padding=ft.padding.symmetric(vertical=2),
            )
        )
        input_ref.current.value = ""
        page.update()

    return ft.Column(
        [
            label_sm("Terminal"),
            ft.Container(height=4),
            display_lg("Shell"),
            ft.Container(height=20),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Container(content=history, height=300, padding=12),
                        ft.Divider(height=1, color=OUTLINE_VAR),
                        ft.Container(
                            content=ft.Row(
                                [
                                    mono("$", color=SECONDARY),
                                    ft.TextField(
                                        ref=input_ref,
                                        hint_text="enter command...",
                                        hint_style=ft.TextStyle(
                                            color=with_opacity(ON_SURFACE_VAR, 0.3)
                                        ),
                                        bgcolor="transparent",
                                        border_color="transparent",
                                        color=ON_SURFACE,
                                        cursor_color=SECONDARY,
                                        text_size=12,
                                        font_family="monospace",
                                        expand=True,
                                        content_padding=0,
                                        on_submit=run_cmd,
                                    ),
                                ],
                                spacing=8,
                            ),
                            padding=12,
                        ),
                    ]
                ),
                bgcolor=SURFACE_LOW,
                border_radius=2,
            ),
        ],
        spacing=0,
    )


def activity_page(page):
    all_logs = [
        ("09:41:02", "OK", "pipeline.run completed"),
        ("09:40:55", "WRN", "memory threshold 78%"),
        ("09:40:48", "OK", "worker:3 spawned"),
        ("09:40:41", "OK", "task queue flushed"),
        ("09:40:33", "ERR", "conn timeout node:7"),
        ("09:40:27", "OK", "auth.refresh success"),
        ("09:40:10", "OK", "db.sync finished"),
        ("09:39:58", "ERR", "rate limit hit on /api/v2"),
        ("09:39:44", "OK", "cache warmed"),
        ("09:39:30", "WRN", "slow query detected 1200ms"),
    ]
    return ft.Column(
        [
            label_sm("System Activity"),
            ft.Container(height=4),
            display_lg("All Events"),
            ft.Container(height=20),
            ft.Container(
                content=ft.Column(
                    [log_entry(t, l, m, i) for i, (t, l, m) in enumerate(all_logs)],
                    spacing=0,
                ),
                bgcolor=SURFACE_LOW,
                padding=20,
                border_radius=2,
            ),
        ],
        spacing=0,
        scroll=ft.ScrollMode.AUTO,
    )


def settings_page(page):
    return ft.Column(
        [
            label_sm("Preferences"),
            ft.Container(height=4),
            display_lg("Settings"),
            ft.Container(height=24),
            ft.Container(
                content=ft.Column(
                    [
                        field_input("API Base URL", "https://api.precision.io/v2"),
                        ft.Container(height=12),
                        field_input("Organization ID", "org_4f9a2b"),
                        ft.Container(height=12),
                        field_input("Log Retention (days)", "30"),
                        ft.Container(height=20),
                        ft.Row(
                            [btn_primary("Save Changes"), btn_ghost("Reset Defaults")],
                            spacing=8,
                        ),
                    ]
                ),
                bgcolor=SURFACE_LOW,
                padding=24,
                border_radius=2,
            ),
        ],
        spacing=0,
    )


def placeholder_page(title, page):
    return ft.Column(
        [
            label_sm(title),
            ft.Container(height=4),
            display_lg(title.title()),
            ft.Container(height=20),
            ft.Container(
                content=ft.Text("Coming soon.", size=13, color=ON_SURFACE_VAR),
                bgcolor=SURFACE_LOW,
                padding=24,
                border_radius=2,
            ),
        ],
        spacing=0,
    )


# ─────────────────────────────────────────────────────────────────────────────
# App Shell with Routing
# ─────────────────────────────────────────────────────────────────────────────


def main(page: ft.Page):
    page.title = "Precis"
    page.bgcolor = SURFACE
    page.padding = 0
    page.theme_mode = ft.ThemeMode.DARK
    page.window.width = 1100
    page.window.height = 700

    page_map = {
        "/dashboard": dashboard_page,
        "/telemetry": telemetry_page,
        "/terminal": terminal_page,
        "/activity": activity_page,
        "/settings": settings_page,
        "/automation": lambda p: placeholder_page("automation", p),
    }

    def route_change(e):
        route = page.route or "/dashboard"
        builder = page_map.get(route, dashboard_page)
        page.controls.clear()
        page.controls.append(
            ft.Row(
                [
                    sidebar(route, page),
                    ft.Container(
                        content=builder(page),
                        expand=True,
                        padding=ft.padding.all(28),
                        bgcolor=SURFACE,
                    ),
                ],
                spacing=0,
                expand=True,
            )
        )
        page.update()

    page.on_route_change = route_change
    page.push_route("/dashboard")


ft.app(target=main)

