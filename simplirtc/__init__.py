from typing import Any, Self, cast

from aiohttp import ClientSession
from simplipy import API
from pydantic.dataclasses import dataclass
from pydantic import TypeAdapter

from .auth import Token

WEBRTC_URL_BASE="https://app-hub.prd.aser.simplisafe.com/v2"


@dataclass(kw_only=True, slots=True)
class LiveViewResponse:
	signedChannelEndpoint: str
	clientId: str
	iceServers: list[Any]


class SimpliRTC(API):
	@classmethod
	async def async_from_token_file(cls: type[Self], path: str, *, session: ClientSession) -> Self:
		api = await cls.async_from_refresh_token(
			await Token.async_load(path),
			session=session,
		)
		api.add_refresh_token_callback(
			lambda refresh_token: Token(refresh_token).async_save(path)
		)
		return cast(Self, api)

	async def async_get_live_view(self, location: str, serial: str) -> LiveViewResponse:
		resp = await self.async_request('get', f'cameras/{serial}/{location}/live-view', url_base=WEBRTC_URL_BASE)
		return TypeAdapter(LiveViewResponse).validate_python(resp)
