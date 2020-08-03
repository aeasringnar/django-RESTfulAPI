from django.test import TestCase
from django.test import Client
import unittest

# Create your tests here.
class TestSubtract(TestCase):

    def test_public_test(self):
        """
        未传参数
        :return:
        """
        res = self.client.get('/test/')
        status_code = res.status_code
        res_data = res.json()
        self.assertEqual(status_code, 200)
        self.assertEqual(res_data.get('errorCode'), 0)

    def test_public_test_params(self):
        """
        传入相关参数
        :return:
        """
        res = self.client.get('/test/', {'page': 1, 'page_size': 10})
        status_code = res.status_code
        res_data = res.json()
        self.assertEqual(status_code, 200)
        self.assertEqual(res_data.get('errorCode'), 0)