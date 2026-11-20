from app.config import settings
from app.platforms.base import BasePlatform
from app.platforms.public import Catbox, Dpaste, Hastebin, PastesDev, Rentry
from app.platforms.social import GitHubGist, Mastodon, Telegram


def build_platforms() -> list[BasePlatform]:
    return [
        Rentry(),
        Dpaste(),
        PastesDev(),
        Hastebin(),
        Catbox(),
        GitHubGist(settings.github_token),
        Telegram(settings.telegram_token, settings.telegram_channel),
        Mastodon(settings.mastodon_instance, settings.mastodon_token),
    ]
