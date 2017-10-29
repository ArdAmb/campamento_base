# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
from base.models import Sensor


class SensorTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_create(self):
        response = self.client.post('/api/sensor/', {'name': 'sensor'})
        self.assertEqual(response.status_code, 403)
        response_json = response.json()
        self.assertIn('detail', response_json)

    def test_create_login(self):
        User.objects.create_superuser('admin', 'admin@test.com', 'admin')
        self.client.login(username='admin', password='admin')
        response = self.client.post('/api/sensor/', {'name': 'sensor'})
        self.assertEqual(response.status_code, 405)
        response_json = response.json()
        self.assertIn('detail', response_json)

    def test_list_empty(self):
        response = self.client.get('/api/sensor/')
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        self.assertIn('count', response_json)
        self.assertEqual(response_json['count'], 0)
        self.assertIn('next', response_json)
        self.assertEqual(response_json['next'], None)
        self.assertIn('previous', response_json)
        self.assertEqual(response_json['previous'], None)
        self.assertIn('results', response_json)

    def test_list(self):
        sensor = Sensor.objects.create(name="sensor")
        response = self.client.get('/api/sensor/')
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        self.assertIn('count', response_json)
        self.assertEqual(response_json['count'], 1)
        self.assertIn('next', response_json)
        self.assertEqual(response_json['next'], None)
        self.assertIn('previous', response_json)
        self.assertEqual(response_json['previous'], None)
        self.assertIn('results', response_json)
        result = response_json['results'][0]
        self.assertIn('name', result)
        self.assertEqual(result['name'], sensor.name)
        self.assertIn('sensor_type', result)
        self.assertEqual(result['sensor_type'], sensor.get_sensor_type_display())
        self.assertIn('url', result)

    def test_update(self):
        sensor = Sensor.objects.create(name="sensor")
        response = self.client.put('/api/sensor/{}/'.format(sensor.pk), {'name': 'sensor_update'})
        self.assertEqual(response.status_code, 403)
        response_json = response.json()
        self.assertIn('detail', response_json)

    def test_update_login(self):
        User.objects.create_superuser('admin', 'admin@test.com', 'admin')
        self.client.login(username='admin', password='admin')
        sensor = Sensor.objects.create(name="sensor")
        response = self.client.put('/api/sensor/{}/'.format(sensor.pk), {'name': 'sensor_update'})
        self.assertEqual(response.status_code, 405)
        response_json = response.json()
        self.assertIn('detail', response_json)

    def test_delete(self):
        sensor = Sensor.objects.create(name="sensor")
        response = self.client.delete('/api/sensor/{}/'.format(sensor.pk))
        self.assertEqual(response.status_code, 403)
        response_json = response.json()
        self.assertIn('detail', response_json)

    def test_delete_login(self):
        User.objects.create_superuser('admin', 'admin@test.com', 'admin')
        self.client.login(username='admin', password='admin')
        sensor = Sensor.objects.create(name="sensor")
        response = self.client.delete('/api/sensor/{}/'.format(sensor.pk))
        self.assertEqual(response.status_code, 405)
        response_json = response.json()
        self.assertIn('detail', response_json)
