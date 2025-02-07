import json
import sys

from aiohttp import ClientSession

from . import SimpliRTC
from .cli import CLI, argument
from .auth import Token, auth_flow


# Initialize CLI instance
cli = CLI(
	argument("--token", type=str, required=True, help="Token file"),
	prog="simplirtc", description="A CLI application for getting SimpliSafe WebRTC streams.",
)


@cli.command(
	argument("--camera", type=str, required=True, help="Camera serial number"),
	argument("--location", type=str, required=True, help="Location ID"),
)
async def stream(token: str, camera: str, location: str) -> int:
	"""Create the aiohttp session and run."""
	async with ClientSession() as session:
		simplirtc = await SimpliRTC.async_from_token_file(token, session=session)
		resp = await simplirtc.async_get_live_view(location, camera)
		GO2RTC_WEBRTC_URI = 'webrtc:{endpoint}#format=kinesis#client_id={client_id}#ice_servers={ice_servers}'
		uri = GO2RTC_WEBRTC_URI.format(
			endpoint = resp.signedChannelEndpoint,
			client_id = resp.clientId,
			ice_servers = json.dumps(resp.iceServers, separators=(',', ':')),
		)

	print(uri)
	return 0


@cli.command()
async def authenticate(token: str) -> int:
	"""Authenticate and save a refresh token."""
	with auth_flow() as (auth_url, verify_code):
		print(f"Please visit {auth_url} to authenticate.")
		refresh_token = await verify_code(input("Enter the code: "))

	await Token(refresh_token).async_save(token)

	print("You are now ready to use the SimpliSafe API!")
	return 0


def main() -> int:
	return cli.run()


if __name__ == "__main__":
	sys.exit(main())
