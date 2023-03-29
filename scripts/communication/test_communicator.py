import unittest
from communicator import (
    CommunicationResponse,
    PropertyType,
    CommunicatorProperty,
    Communicator,
)


class TestCommunicationResponse(unittest.TestCase):
    def test_init_and_str(self):
        response = CommunicationResponse(200, "OK")
        self.assertEqual(response.code, 200)
        self.assertEqual(response.payload, "OK")
        self.assertEqual(str(response), "[200]\nOK")

    def test_get_code(self):
        response = CommunicationResponse(200, "OK")
        self.assertEqual(response.get_code(), 200)

    def test_get_payload(self):
        response = CommunicationResponse(200, "OK")
        self.assertEqual(response.get_payload(), "OK")


class TestPropertyType(unittest.TestCase):
    def test_choices(self):
        expected_choices = [
            (PropertyType.int.value, PropertyType.int.name),
            (PropertyType.float.value, PropertyType.float.name),
            (PropertyType.str.value, PropertyType.str.name),
        ]
        self.assertEqual(PropertyType.choices(), expected_choices)


class TestCommunicatorProperty(unittest.TestCase):
    def test_init(self):
        prop = CommunicatorProperty(
            "test_name",
            PropertyType.int,
            mandatory=True,
            default=0,
            configuration="test_config",
        )
        self.assertEqual(prop.name, "test_name")
        self.assertEqual(prop.type, PropertyType.int)
        self.assertEqual(prop.mandatory, True)
        self.assertEqual(prop.default, 0)
        self.assertEqual(prop.configuration, "test_config")

    def test_fetch_default_value(self):
        prop1 = CommunicatorProperty("prop1", PropertyType.int, True, 10, "config1")
        prop2 = CommunicatorProperty("prop2", PropertyType.float, False, 3.14, "config2")
        prop3 = CommunicatorProperty("prop3", PropertyType.str, True, "default", "config3")

        props = [prop1, prop2, prop3]

        self.assertEqual(CommunicatorProperty.fetch_default_value(props, "prop1"), 10)
        self.assertEqual(CommunicatorProperty.fetch_default_value(props, "prop2"), 3.14)
        self.assertEqual(CommunicatorProperty.fetch_default_value(props, "prop3"), "default")
        self.assertEqual(CommunicatorProperty.fetch_default_value(props, "unknown_prop"), -1)


if __name__ == "__main__":
    unittest.main()