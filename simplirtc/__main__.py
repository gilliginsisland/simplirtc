import json

from aiohttp import ClientSession
from simplipy.system.v3 import SystemV3

from . import SimpliRTC
from .cli import CLI, argument
from .auth import Token, auth_flow


# Initialize CLI instance
cli = CLI(
	argument("--token", type=str, required=True, help="Token file"),
	prog="simplirtc", description="A CLI application for getting SimpliSafe WebRTC streams.",
)


@cli.command()
async def authenticate(token: str) -> None:
	"""Authenticate and save a refresh token."""
	with auth_flow() as (auth_url, verify_code):
		print(f"Please visit {auth_url} to authenticate.")
		refresh_token = await verify_code(input("Enter the code: "))

	await Token(refresh_token).async_save(token)

	print("You are now ready to use the SimpliSafe API!")


@cli.command()
async def cameras(token: str) -> None:
	"""List devices."""
	async with ClientSession() as session:
		simplirtc = await SimpliRTC.async_from_token_file(token, session=session)
		systems = await simplirtc.async_get_systems()

	data = {
		f"{system.address} ({system_id})": [
			f"{camera.name} ({camera_id})"
			for camera_id, camera in system.cameras.items()
		]
		for system_id, system in systems.items()
		if isinstance(system, SystemV3)
	}

	print(json.dumps(data, indent=2, default=str))


@cli.command(
	argument("--camera", type=str, required=True, help="Camera serial number"),
	argument("--location", type=str, required=True, help="Location ID"),
)
async def stream(token: str, camera: str, location: str) -> None:
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


def main() -> int:
	return cli.run()


if __name__ == "__main__":
	main()
