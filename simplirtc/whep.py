import re

from aiohttp import web
import boto3

from . import SimpliRTC

SIMPLISAFE = web.AppKey('SIMPLISAFE', SimpliRTC)


def extract_arn_region(channel_arn: str) -> str | None:
	if (match := re.search(r"kinesisvideo:([a-z\-0-9]+):", channel_arn)):
		return match.group(1)


class CameraDeviceView(web.View):
	@property
	def simplisafe(self) -> SimpliRTC:
		return self.request.app[SIMPLISAFE]

	@property
	def location_id(self) -> str:
		return self.request.match_info["location_id"]

	@property
	def device_id(self) -> str:
		return self.request.match_info["device_id"]


class WebRTCHandler(CameraDeviceView):
	async def post(self) -> web.Response:
		sdp_offer = await self.request.text()
		if not sdp_offer:
			return web.json_response({"error": "Missing SDP offer"}, status=400)

		live_view = await self.simplisafe.async_get_live_view(self.location_id, self.device_id)
		client_id = live_view.clientId
		channel_arn = live_view.signedChannelEndpoint
		if not (region := extract_arn_region(channel_arn)):
			return web.json_response({"error": "Invalid ChannelARN"}, status=400)

		kvs_webrtc_client = boto3.client("kinesis-video-webrtc-storage", region_name=region)
		response = kvs_webrtc_client.start_sdp_answer(
			ChannelARN=channel_arn,
			Answer={"Type": "ANSWER", "SDP": sdp_offer},
			ClientId=client_id,
		)
		sdp_answer = response.get("Answer", {}).get("SDP", "")

		return web.Response(text=sdp_answer, content_type="application/sdp")


def create_whep_app(simplisafe: SimpliRTC) -> web.Application:
	app = web.Application()
	app[SIMPLISAFE] = simplisafe
	app.router.add_view("/{location_id}/{device_id}/whep", WebRTCHandler)
	return app
