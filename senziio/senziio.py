"""API for interacting with Senziio Devices."""

import asyncio
import json
import logging
from abc import ABC

logger = logging.getLogger(__name__)


class SenziioMQTT(ABC):
    """Senziio MQTT communication interface."""

    @abstractmethod
    async def publish(self, topic, payload):
        """Publish to topic with a payload."""

    @abstractmethod
    async def subscribe(self, topic, callback):
        """Subscribe to topic with a callback."""


class Senziio:
    """Senziio device communications."""

    TIMEOUT = 10

    def __init__(self, device_id: str, device_model: str, mqtt: SenziioMQTT) -> None:
        """Initialize instance."""
        self.device_id = device_id
        self.model_key = "-".join(device_model.lower().split())
        self.mqtt = mqtt
        self.topics = {
            "info_req": f"cmd/{self.model_key}/{device_id}/device-info/req",
            "info_res": f"cmd/{self.model_key}/{device_id}/device-info/res",
            "data": f"dt/{self.model_key}/{device_id}",
        }

    @property
    def id(self):
        """Return ID of device."""
        return self.device_id

    async def get_info(self):
        """Get device info."""
        device_info = {}
        response = asyncio.Event()

        async def handle_response(message):
            """Handle device info response."""
            nonlocal device_info
            try:
                device_info = json.loads(message.payload)
            except json.JSONDecodeError:
                logger.error(
                    "Could not parse device info payload: %s", message.payload
                )
            response.set()

        unsubscribe_callback = await self.mqtt.subscribe(
            self.topics["info_res"],
            handle_response,
        )

        await self.mqtt.publish(
            self.topics["info_req"],
            "Device info request",
        )

        try:
            await asyncio.wait_for(response.wait(), self.TIMEOUT)
            return device_info
        except TimeoutError:
            return None
        finally:
            unsubscribe_callback()

    def entity_topic(self, entity: str) -> str:
        """Get topic for listening to entity data updates."""
        return f"{self.topics['data']}/{entity}"
