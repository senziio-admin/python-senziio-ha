from unittest.mock import Mock

from senziio import Senziio


def test_device_id_attribute():
    device_id = "a-device-id"
    device_model = "a-device-model"

    device = Senziio(device_id, device_model, mqtt=Mock())

    assert device.id == device_id
