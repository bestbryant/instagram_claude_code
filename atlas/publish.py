"""Publish through Instagram's official Graph API (Content Publishing).

Needs a Professional (Creator or Business) Instagram account and a long-lived
access token. No passwords are ever used. Media must be reachable at public
URLs; images must be JPEG.

Environment:
  IG_USER_ID       the Instagram professional account id
  IG_ACCESS_TOKEN  long-lived token with instagram_business_content_publish
                   (or instagram_content_publish via Facebook Login)
  IG_GRAPH_HOST    graph.instagram.com (Instagram Login, default) or
                   graph.facebook.com (Facebook Login)
  IG_API_VERSION   default v23.0
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request


class GraphError(RuntimeError):
    pass


class Publisher:
    def __init__(self, user_id=None, token=None, host=None, version=None, dry_run=False):
        self.user_id = user_id or os.environ.get("IG_USER_ID", "")
        self.token = token or os.environ.get("IG_ACCESS_TOKEN", "")
        self.host = host or os.environ.get("IG_GRAPH_HOST", "graph.instagram.com")
        self.version = version or os.environ.get("IG_API_VERSION", "v23.0")
        self.dry_run = dry_run
        if not dry_run and not (self.user_id and self.token):
            raise GraphError("Set IG_USER_ID and IG_ACCESS_TOKEN (see docs/PUBLISHING.md).")
        if dry_run and not self.user_id:
            self.user_id = "<IG_USER_ID>"
        self._fake = 0

    def _call(self, method, path, **params):
        url = f"https://{self.host}/{self.version}/{path}"
        if self.dry_run:
            shown = {k: (v[:60] + "…" if isinstance(v, str) and len(v) > 60 else v) for k, v in params.items()}
            print(f"[dry-run] {method} {url} {json.dumps(shown, ensure_ascii=False)}")
            self._fake += 1
            return {"id": f"dry{self._fake}", "status_code": "FINISHED"}
        params["access_token"] = self.token
        data = urllib.parse.urlencode(params).encode()
        if method == "GET":
            req = urllib.request.Request(url + "?" + data.decode())
        else:
            req = urllib.request.Request(url, data=data, method=method)
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            raise GraphError(f"{e.code} {e.read().decode(errors='replace')}") from None

    def _wait(self, container, timeout=600):
        start = time.time()
        while True:
            st = self._call("GET", container, fields="status_code,status").get("status_code")
            if st == "FINISHED":
                return
            if st in ("ERROR", "EXPIRED"):
                raise GraphError(f"container {container} {st}")
            if time.time() - start > timeout:
                raise GraphError(f"container {container} not ready after {timeout}s")
            time.sleep(5)

    def _publish(self, container):
        self._wait(container)
        return self._call("POST", f"{self.user_id}/media_publish", creation_id=container)["id"]

    def carousel(self, image_urls, caption):
        children = [self._call("POST", f"{self.user_id}/media", image_url=u, is_carousel_item="true")["id"]
                    for u in image_urls]
        for c in children:
            self._wait(c)
        parent = self._call("POST", f"{self.user_id}/media", media_type="CAROUSEL",
                            children=",".join(children), caption=caption)["id"]
        return self._publish(parent)

    def image(self, image_url, caption):
        c = self._call("POST", f"{self.user_id}/media", image_url=image_url, caption=caption)["id"]
        return self._publish(c)

    def reel(self, video_url, caption, cover_url=None, audio_name=None):
        params = dict(media_type="REELS", video_url=video_url, caption=caption, share_to_feed="true")
        if cover_url:
            params["cover_url"] = cover_url
        if audio_name:
            params["audio_name"] = audio_name      # names the original audio; can only be set once
        try:
            c = self._call("POST", f"{self.user_id}/media", **params)["id"]
        except GraphError as e:
            if not audio_name or "audio" not in str(e).lower():
                raise
            params.pop("audio_name")
            c = self._call("POST", f"{self.user_id}/media", **params)["id"]
        return self._publish(c)

    def reel_file(self, path, caption, cover_url=None):
        """Upload a local video straight to Meta (resumable upload), no public URL needed."""
        params = dict(media_type="REELS", upload_type="resumable", caption=caption, share_to_feed="true")
        if cover_url:
            params["cover_url"] = cover_url
        c = self._call("POST", f"{self.user_id}/media", **params)
        container = c["id"]
        uri = c.get("uri") or f"https://rupload.facebook.com/ig-api-upload/{self.version}/{container}"
        data = open(path, "rb").read()
        if self.dry_run:
            print(f"[dry-run] POST {uri} ({len(data):,} bytes)")
        else:
            req = urllib.request.Request(uri, data=data, method="POST", headers={
                "Authorization": f"OAuth {self.token}", "offset": "0", "file_size": str(len(data))})
            try:
                with urllib.request.urlopen(req, timeout=300) as r:
                    json.loads(r.read())
            except urllib.error.HTTPError as e:
                raise GraphError(f"upload {e.code} {e.read().decode(errors='replace')}") from None
        return self._publish(container)

    def username(self):
        return self._call("GET", self.user_id, fields="username").get("username", "")

    def recent_media(self, limit=10):
        return self._call("GET", f"{self.user_id}/media", fields="id,caption,timestamp,permalink", limit=limit).get("data", [])

    def comment(self, media_id, message):
        return self._call("POST", f"{media_id}/comments", message=message)["id"]

    def recent_comments(self, media_id):
        return self._call("GET", f"{media_id}/comments", fields="id,text,username,timestamp").get("data", [])
