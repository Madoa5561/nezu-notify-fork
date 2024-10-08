import json
import logging
from typing import Dict, List, Optional

import requests

from .urls import APIUrls


class GroupManager:
    def __init__(self, csrf: str, cookie: str):
        self.session = requests.Session()
        self.csrf = csrf
        self.cookie = cookie
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
            "Referer": "https://notify-bot.line.me/my/",
            "X-Requested-With": "XMLHttpRequest",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "X-CSRF-Token": self.csrf,
            "Cookie": self.cookie,
        }

    def get_groups(self) -> List[Dict[str, str]]:
        logging.info(f"Requesting groups from: {APIUrls.GROUP_LIST_URL}")
        logging.info(f"Headers: {self.headers}")

        response = self._make_request(APIUrls.GROUP_LIST_URL)
        if response:
            logging.info(f"Response status code: {response.status_code}")
            logging.info(f"Response content: {response.text}")

            if response.status_code == 200:
                try:
                    data = response.json()
                    groups = data.get("results", [])
                    logging.info(f"Received {len(groups)} groups")
                    return groups
                except json.JSONDecodeError:
                    logging.error("JSONのデコードに失敗しました。")
            else:
                logging.error(
                    f"グループの取得に失敗しました。ステータスコード: {response.status_code}"
                )
        else:
            logging.error("APIリクエストに失敗しました。")
        return []

    def create_token(
        self, description: str, target_type: str, target_mid: str
    ) -> Optional[str]:
        url = "https://notify-bot.line.me/api/token"
        data = {
            "action": "issuePersonalAcessToken",
            "description": description,
            "targetType": target_type,
            "targetMid": target_mid,
            "_csrf": self.csrf,
        }

        response = self._make_request(url, method="POST", data=data)
        if response and response.status_code == 200:
            try:
                result = response.json()
                return result.get("token")
            except json.JSONDecodeError:
                logging.error("JSONのデコードに失敗しました。")
        else:
            logging.error(
                f"トークンの作成に失敗しました。ステータスコード: {response.status_code if response else 'Unknown'}"
            )
        return None

    def get_group_by_mid(self, mid: str) -> Optional[Dict[str, str]]:
        groups = self.get_groups()
        for group in groups:
            if group["mid"] == mid:
                return group
        logging.warning(f"Group with MID: {mid} not found.")
        return None

    def _make_request(
        self, endpoint: str, method: str = "GET", data: Optional[Dict] = None
    ) -> Optional[requests.Response]:
        method = method.upper()
        if method not in {"GET", "POST"}:
            raise ValueError(f"Invalid HTTP method specified: {method}")

        try:
            response = requests.request(
                method, endpoint, headers=self.headers, data=data
            )
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logging.error(
                f"HTTP request error - URL: {endpoint}, Method: {method}, Error: {e}"
            )
            if hasattr(e, "response"):
                logging.error(f"エラーレスポンス: {e.response.text}")
            return None
