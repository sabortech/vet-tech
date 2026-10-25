import reflex as rx

config = rx.Config(
    app_name="vet_tech",
    show_built_with_reflex=False,
    static_page_generation_timeout=180,
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
        rx.plugins.RadixThemesPlugin(theme=rx.theme(appearance="inherit", accent_color="grass")),
    ]
)