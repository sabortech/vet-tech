import reflex as rx

config = rx.Config(
    app_name="vet_tech",
    static_page_generation_timeout=180,
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
        rx.plugins.RadixThemesPlugin(),
    ]
)