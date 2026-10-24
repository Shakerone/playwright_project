from playwright.sync_api import Page


def mock_static_resources(page: Page):
    page.route("**/*.{ico,png,jpg,webp,mp3,mp4,woff,woff2}", lambda route: route.abort())
