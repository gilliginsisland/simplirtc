from typing import Self

import asyncio
import json
import argparse

import aiofiles
from aiohttp import ClientSession
from simplipy import API


WEBRTC_URL_BASE="https://app-hub.prd.aser.simplisafe.com/v2"


class Simplisafe:
	@classmethod
	async def async_from_token_file(cls: type[Self], path: str, *, session: ClientSession):
		async def async_save_refresh_token(token: str):
			async with aiofiles.open(path, mode="w") as f:
				await f.write(token)

		async with aiofiles.open(path, mode="r") as f:
			token = await f.read()

		api = await API.async_from_refresh_token(
			token, session=session
		)
		api.add_refresh_token_callback(async_save_refresh_token)

		return cls(api=api)

	def __init__(self, *, api: API) -> None:
		self._api: API = api

	async def async_get_live_stream_url(self, location: str, serial: str):
		resp = await self._api.async_request('get', f'cameras/{serial}/{location}/live-view', url_base=WEBRTC_URL_BASE)

		endpoint = resp['signedChannelEndpoint']
		client_id = resp['clientId']
		ice_servers = json.dumps(resp['iceServers'], separators=(',', ':'))
		url = f'webrtc:{endpoint}#format=kinesis#client_id={client_id}#ice_servers={ice_servers}'

		return url


async def main():
	parser = argparse.ArgumentParser(description="Set camera serial and location ID.")
	parser.add_argument("--token", type=str, required=True, help="Token file")
	parser.add_argument("--camera", type=str, required=True, help="Camera serial number")
	parser.add_argument("--location", type=str, required=True, help="Location ID")

	args = parser.parse_args()

	# Assign variables from command line arguments
	camera_serial = args.camera
	location_id = args.location
	token_file = args.token

	"""Create the aiohttp session and run."""
	async with ClientSession() as session:
		simplisafe = await Simplisafe.async_from_token_file(token_file, session=session)
		resp = await simplisafe.async_get_live_stream_url(location_id, camera_serial)
		print(resp)


if __name__ == "__main__":
	asyncio.run(main())
