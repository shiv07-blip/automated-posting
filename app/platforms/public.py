import httpx

from app.platforms.base import BasePlatform


class Rentry(BasePlatform):
    name = "Rentry"

    def post(self, message: str, client: httpx.Client) -> str:
        response = client.post("https://rentry.co/api/new", data={"text": message})
        self.check(response)
        payload = response.json()
        if payload.get("status") != "200":
            raise RuntimeError(f"Rentry API: {payload.get('content', payload)}")
        return payload["url"]


class Dpaste(BasePlatform):
    name = "dpaste.org"

    def post(self, message: str, client: httpx.Client) -> str:
        response = client.post(
            "https://dpaste.org/api/",
            data={"format": "url", "content": message, "expires": "604800"},
        )
        self.check(response)
        return response.text.strip().strip('"')


class PastesDev(BasePlatform):
    name = "Pastes.dev"

    def post(self, message: str, client: httpx.Client) -> str:
        response = client.post(
            "https://api.pastes.dev/post",
            content=message,
            headers={"Content-Type": "text/plain"},
        )
        self.check(response)
        return f"https://pastes.dev/{response.json()['key']}"


class Hastebin(BasePlatform):
    name = "Hastebin"

    def post(self, message: str, client: httpx.Client) -> str:
        response = client.post(
            "https://hst.sh/documents",
            content=message,
            headers={"Content-Type": "text/plain"},
        )
        self.check(response)
        return f"https://hst.sh/{response.json()['key']}"


class Catbox(BasePlatform):
    name = "Catbox.moe"

    def post(self, message: str, client: httpx.Client) -> str:
        response = client.post(
            "https://catbox.moe/user/api.php",
            data={"reqtype": "fileupload"},
            files={"fileToUpload": ("message.txt", message, "text/plain")},
        )
        self.check(response)
        url = response.text.strip()
        if not url.startswith("https://"):
            raise RuntimeError(f"Catbox API: {url[:200]}")
        return url
