from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

User = get_user_model()


class UsersAPITestCase(APITestCase):
    url = reverse('users:create-list')

    user_data = {
        'username': 'testuser@test.ru',
        'password': 'testPasswordStrong#!@$2',
        'first_name': 'Test',
        'last_name': 'Userovich',
        'inn': '12345',
        'balance': 100
    }

    def tearDown(self):
        User.objects.all().delete()

    def test_create_user(self):
        response = self.client.post(self.url, self.user_data)
        resp_data = response.json()
        self.assertEqual(201, response.status_code)
        self.assertTrue(self.user_data.get('inn') == resp_data.get('inn'))
        self.assertFalse(12345 == resp_data.get('inn'))
        self.assertTrue(self.user_data.get('balance') == resp_data.get('balance'))
        users = User.objects.all()
        self.assertEqual(1, users.count())
        user = users.first()
        self.assertTrue(user.check_password(self.user_data.get('password')))


class UsersSendAPITestCase(APITestCase):
    send_data = {
        "inns": ["11111"],
        "amount": 10
    }
    user_data = {
        'username': 'user1',
        'password': 'testPasswordStrong#!@$2',
        'first_name': 'Test',
        'last_name': 'Userovich',
        'inn': '11111',
        'balance': 100
    }

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(**self.user_data)

        self.user_data['username'] = 'user2'
        self.user_data['inn'] = '22222'
        self.user_data['balance'] = 0

        self.user2 = User.objects.create_user(**self.user_data)

        self.user_data['username'] = 'user3'
        self.user_data['inn'] = '33333'
        self.user3 = User.objects.create_user(**self.user_data)

        self.user_data['username'] = 'user4'
        self.user_data['inn'] = '44444'
        self.user_data['balance'] = 100
        self.user4 = User.objects.create_user(**self.user_data)

        self.user_data['username'] = 'user5'
        self.user_data['inn'] = '44444'
        self.user_data['balance'] = 50
        self.user5 = User.objects.create_user(**self.user_data)

    def test_send_to_users(self):
        self.send_data['inns'] = [self.user2.inn, self.user3.inn]
        send_url = reverse('users:send-to-users', kwargs={'user_id': self.user.id})
        resp_data = self.client.put(send_url, self.send_data).json()
        user_balance = User.objects.get(id=self.user.id).balance
        user2_balance = User.objects.get(id=self.user2.id).balance
        user3_balance = User.objects.get(id=self.user3.id).balance
        sum_to_user = Decimal(self.send_data['amount'] / len(self.send_data['inns']))
        self.assertTrue(
            user_balance == self.user.balance - self.send_data['amount'])
        self.assertTrue(
            user2_balance == self.user2.balance + sum_to_user)
        self.assertTrue(
            user3_balance == self.user3.balance + sum_to_user)

    def test_failed_data(self):
        send_url = reverse('users:send-to-users', kwargs={'user_id': self.user.id})

        # empty inns
        self.send_data['inns'] = []
        resp_data = self.client.put(send_url, self.send_data)
        self.assertTrue(400 == resp_data.status_code)

        # self inn
        self.send_data['inns'] = [self.user.inn]
        resp_data = self.client.put(send_url, self.send_data)
        self.assertTrue(400 == resp_data.status_code)

        # inn does not exists
        self.send_data['inns'] = ['77777']
        resp_data = self.client.put(send_url, self.send_data)
        self.assertTrue(400 == resp_data.status_code)

        # inn exists and not exists
        self.send_data['inns'] = [self.user2.inn, '77777']
        resp_data = self.client.put(send_url, self.send_data)
        self.assertTrue(200 == resp_data.status_code)

        user_balance = User.objects.get(id=self.user.id).balance
        user2_balance = User.objects.get(id=self.user2.id).balance
        self.assertTrue(
            user_balance == self.user.balance - self.send_data['amount'])
        self.assertTrue(
            user2_balance == self.user2.balance + self.send_data['amount'])

    def test_amount(self):
        send_url = reverse('users:send-to-users', kwargs={'user_id': self.user.id})
        # amount>balance
        self.send_data['inns'] = [self.user2.inn]
        self.send_data['amount'] = self.user.balance + 1
        resp_data = self.client.put(send_url, self.send_data)
        self.assertTrue(400 == resp_data.status_code)
