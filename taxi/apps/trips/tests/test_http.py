import base64
import json

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from taxi.apps.trips.models import Trip

PASSWORD = 'pAssw0rd'


def create_user(username='user@example.com', password=PASSWORD):  # new
    return get_user_model().objects.create_user(
        username=username,
        first_name='Test',
        last_name='User',
        password=password
    )


class AuthenticationTest(APITestCase):
    def test_user_can_sign_up(self):
        response = self.client.post(reverse('sign_up'), data={
            'username': 'user@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': PASSWORD,
            'password2': PASSWORD,
        })

        user = get_user_model().objects.last()
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(response.data['id'], user.id)
        self.assertEqual(response.data['username'], user.username)
        self.assertEqual(response.data['first_name'], user.first_name)
        self.assertEqual(response.data['last_name'], user.last_name)

    def test_user_with_bad_password_not_created(self):
        response = self.client.post(reverse('sign_up'), data={
            'username': 'user@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': PASSWORD,
            'password2': 'PASSWORD',
        })

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(response.data['non_field_errors'][0], 'Passwords must match.')

    def test_user_with_repeated_username_not_created(self):
        get_user_model().objects.create_user(**{
            'username': 'user@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': PASSWORD,
        })
        response = self.client.post(reverse('sign_up'), data={
            'username': 'user@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': PASSWORD,
            'password2': PASSWORD,
        })
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(response.data['username'][0], 'A user with that username already exists.')

    def test_user_can_log_in(self):
        user = create_user()
        response = self.client.post(reverse('log_in'), data={'username': user.username, 'password': PASSWORD})

        access = response.data['access']
        header, payload, signature = access.split('.')
        decoded_payload = base64.b64decode(f'{payload}==')
        payload_data = json.loads(decoded_payload)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIsNotNone(response.data['refresh'])
        self.assertEqual(payload_data['id'], user.id)
        self.assertEqual(payload_data['username'], user.username)
        self.assertEqual(payload_data['first_name'], user.first_name)
        self.assertEqual(payload_data['last_name'], user.last_name)


class HttpTripTest(APITestCase):
    def setUp(self):
        user = create_user()
        response = self.client.post(reverse('log_in'), data={'username': user.username, 'password': PASSWORD})
        self.access = response.data['access']

    def test_user_can_list_trips(self):
        trips = [
            Trip.objects.create(pick_up_address='A', drop_off_address='B'),
            Trip.objects.create(pick_up_address='A', drop_off_address='C')
        ]

        response = self.client.get(reverse('trip:trip_list'), HTTP_AUTHORIZATION=f'Bearer {self.access}')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        expected_trip_ids = [str(trip.id) for trip in trips]
        actual_trip_ids = [trip.get('id') for trip in response.data]
        self.assertCountEqual(expected_trip_ids, actual_trip_ids)

    def test_user_can_retrieve_trip_by_id(self):
        trip = Trip.objects.create(pick_up_address='A', drop_off_address='B')
        response = self.client.get(trip.get_absolute_url(),
                                   HTTP_AUTHORIZATION=f'Bearer {self.access}'
                                   )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(str(trip.id), response.data.get('id'))
