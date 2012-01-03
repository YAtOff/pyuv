
import os

import common
import pyuv


TEST_PORT = 12345
TEST_PORT2 = 12346
MULTICAST_ADDRESS = "239.255.0.1"

class UDPTest(common.UVTestCase):

    def setUp(self):
        self.loop = pyuv.Loop.default_loop()
        self.server = None
        self.client = None

    def on_close(self, handle):
        self.on_close_called += 1

    def on_server_recv(self, handle, (ip, port), data):
        data = data.strip()
        self.assertEquals(data, "PING")
        self.server.send("PONG"+os.linesep, (ip, port))

    def on_client_recv(self, handle, (ip, port), data):
        data = data.strip()
        self.assertEquals(data, "PONG")
        self.client.close(self.on_close)
        self.server.close(self.on_close)

    def timer_cb(self, timer):
        self.client.send("PING"+os.linesep, ("127.0.0.1", TEST_PORT))
        timer.close(self.on_close)

    def test_udp_pingpong(self):
        self.on_close_called = 0
        self.server = pyuv.UDP(self.loop)
        self.server.bind(("0.0.0.0", TEST_PORT))
        self.server.start_recv(self.on_server_recv)
        self.client = pyuv.UDP(self.loop)
        self.client.bind(("0.0.0.0", TEST_PORT2))
        self.client.start_recv(self.on_client_recv)
        timer = pyuv.Timer(self.loop)
        timer.start(self.timer_cb, 0.1, 0)
        self.loop.run()
        self.assertEqual(self.on_close_called, 3)


class UDPTestList(common.UVTestCase):

    def setUp(self):
        self.loop = pyuv.Loop.default_loop()
        self.server = None
        self.client = None

    def on_close(self, handle):
        self.on_close_called += 1

    def on_server_recv(self, handle, (ip, port), data):
        data = data.strip()
        self.assertEquals(data, "PING")
        self.server.send(["PONG", os.linesep], (ip, port))

    def on_client_recv(self, handle, (ip, port), data):
        data = data.strip()
        self.assertEquals(data, "PONG")
        self.client.close(self.on_close)
        self.server.close(self.on_close)

    def timer_cb(self, timer):
        self.client.send(["PING", os.linesep], ("127.0.0.1", TEST_PORT))
        timer.close(self.on_close)

    def test_udp_pingpong(self):
        self.on_close_called = 0
        self.server = pyuv.UDP(self.loop)
        self.server.bind(("0.0.0.0", TEST_PORT))
        self.server.start_recv(self.on_server_recv)
        self.client = pyuv.UDP(self.loop)
        self.client.bind(("0.0.0.0", TEST_PORT2))
        self.client.start_recv(self.on_client_recv)
        timer = pyuv.Timer(self.loop)
        timer.start(self.timer_cb, 0.1, 0)
        self.loop.run()
        self.assertEqual(self.on_close_called, 3)


class UDPTestMulticast(common.UVTestCase):

    def setUp(self):
        self.loop = pyuv.Loop.default_loop()
        self.server = None
        self.client = None
        self.received_data = None

    def on_close(self, handle):
        self.on_close_called += 1

    def on_client_recv(self, handle, (ip, port), data):
        self.received_data = data.strip()
        self.client.set_membership(MULTICAST_ADDRESS, pyuv.UV_LEAVE_GROUP)
        self.client.close(self.on_close)

    def on_server_send(self, handle, status):
        handle.close(self.on_close)

    def test_udp_multicast(self):
        self.on_close_called = 0
        self.server = pyuv.UDP(self.loop)
        self.client = pyuv.UDP(self.loop)
        self.client.bind((MULTICAST_ADDRESS, TEST_PORT))
        self.client.set_membership(MULTICAST_ADDRESS, pyuv.UV_JOIN_GROUP)
        self.client.start_recv(self.on_client_recv)
        self.server.send("PING", (MULTICAST_ADDRESS, TEST_PORT), self.on_server_send)
        self.loop.run()
        self.assertEqual(self.on_close_called, 2)
        self.assertEquals(self.received_data, "PING")


if __name__ == '__main__':
    import unittest
    tests = unittest.TestSuite(common.suites)
    unittest.TextTestRunner(verbosity=2).run(tests)

