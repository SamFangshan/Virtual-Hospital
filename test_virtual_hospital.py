import unittest


class VirtualHospitalTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    # sample test case
    def test_hello_world(self):
        greeting = 'Hello world!'
        self.assertEqual(greeting, 'Hello world!')


if __name__ == '__main__':
    unittest.main()
