import time
from http import HTTPStatus
from typing import Annotated

import requests
import requests_cache

from pylastfm.constants import URL

T_Response = Annotated[
    requests_cache.models.response.OriginalResponse,
    requests_cache.models.response.CachedResponse,
]


class RequestController:
    def __init__(
        self, user_agent: str, api_key: str, reset_cache: bool = False
    ) -> None:
        self.headers = {'user-agent': user_agent}
        self.payload = {'api_key': api_key, 'format': 'json'}
        requests_cache.install_cache()
        if reset_cache:
            self.clear_cache()

    def request(self, payload: dict) -> T_Response:
        self.payload.update(payload)
        response = requests.get(URL, headers=self.headers, params=self.payload)
        return response

    def clear_cache(self) -> None:
        cache = self.requests_cache.get_cache()
        cache.clear()

    def request_all_pages(
        self, payload: dict, parent_key: str, list_key: str
    ) -> list[T_Response]:
        responses = []
        page = 1
        while True:
            payload['page'] = page
            response = self.request(payload)

            if response.status_code != HTTPStatus.OK:
                print(response.status_code, response.text)
                break
            if len(response.json()[parent_key][list_key]) == 0:
                print('No more results, but there are more pages')
                break

            if not getattr(response, 'from_cache', False):
                time.sleep(0.25)
            responses.append(response)
            page += 1

            if page > int(response.json()[parent_key]['@attr']['totalPages']):
                break
        return responses
