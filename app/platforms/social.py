import httpx

from app.platforms.base import BasePlatform


class GitHubGist(BasePlatform):
    name = "GitHub Gist"

    def __init__(self, token: str | None) -> None:
        self.token = token

    def post(self, message: str, client: httpx.Client) -> str:
        if not self.token:
            raise RuntimeError("GITHUB_TOKEN is not configured")
        response = client.post(
            "https://api.github.com/gists",
            json={
                "description": "Multi-platform posting API",
                "public": True,
                "files": {"message.txt": {"content": message}},
            },
            headers={
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        self.check(response)
        return response.json()["html_url"]


class Telegram(BasePlatform):
    name = "Telegram Channel"

    def __init__(self, token: str | None, channel: str | None) -> None:
        self.token = token
        self.channel = channel

    def post(self, message: str, client: httpx.Client) -> str:
        if not (self.token and self.channel):
            raise RuntimeError("TELEGRAM_TOKEN and TELEGRAM_CHANNEL are not configured")
        response = client.post(
            f"https://api.telegram.org/bot{self.token}/sendMessage",
            json={"chat_id": self.channel, "text": message},
        )
        self.check(response)
        payload = response.json()
        if not payload.get("ok"):
            raise RuntimeError(f"Telegram API: {payload.get('description', payload)}")
        message_id = payload["result"]["message_id"]
        return f"https://t.me/{self.channel.lstrip('@')}/{message_id}"


class Mastodon(BasePlatform):
    name = "Mastodon"

    def __init__(self, instance: str | None, token: str | None) -> None:
        self.instance = instance
        self.token = token

    def post(self, message: str, client: httpx.Client) -> str:
        if not (self.instance and self.token):
            raise RuntimeError("MASTODON_INSTANCE and MASTODON_TOKEN are not configured")
        response = client.post(
            f"https://{self.instance}/api/v1/statuses",
            json={"status": message, "visibility": "public"},
            headers={"Authorization": f"Bearer {self.token}"},
        )
        self.check(response)
        return response.json()["url"]
