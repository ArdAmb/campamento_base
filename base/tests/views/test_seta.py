# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
from base.models import Seta, Sensor


class SetaTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_create(self):
        response = self.client.post('/api/seta/', {'name': 'seta'})
        self.assertEqual(response.status_code, 403)
        response_json = response.json()
        self.assertIn('detail', response_json)

    def test_create_login(self):
        User.objects.create_superuser('admin', 'admin@test.com', 'admin')
        self.client.login(username='admin', password='admin')
        response = self.client.post('/api/seta/', {'name': 'seta'})
        self.assertEqual(response.status_code, 405)
        response_json = response.json()
        self.assertIn('detail', response_json)

    def test_list_empty(self):
        response = self.client.get('/api/seta/')
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
        seta = Seta.objects.create(name="seta")
        response = self.client.get('/api/seta/')
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
        self.assertEqual(result['name'], seta.name)
        self.assertIn('sensors', result)
        self.assertEqual(result['sensors'], [])
        self.assertIn('url', result)

    def test_list_with_sensors(self):
        sensor = Sensor.objects.create(name="sensor")
        seta = Seta.objects.create(name="seta")
        seta.sensors.add(sensor)
        response = self.client.get('/api/seta/')
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        self.assertIn('results', response_json)
        result = response_json['results'][0]
        self.assertIn('name', result)
        self.assertEqual(result['name'], seta.name)
        self.assertIn('sensors', result)
        self.assertIn('url', result)
        # The other data are checking already on test_list
        sensor_result = result['sensors'][0]
        self.assertIn('name', sensor_result)
        self.assertEqual(sensor_result['name'], sensor.name)
        self.assertNotIn('sensor_type', sensor_result)
        self.assertIn('url', sensor_result)

    def test_update(self):
        seta = Seta.objects.create(name="seta")
        response = self.client.put('/api/seta/{}/'.format(seta.pk), {'name': 'seta_update'})
        self.assertEqual(response.status_code, 403)
        response_json = response.json()
        self.assertIn('detail', response_json)

    def test_update_login(self):
        User.objects.create_superuser('admin', 'admin@test.com', 'admin')
        self.client.login(username='admin', password='admin')
        seta = Seta.objects.create(name="seta")
        response = self.client.put('/api/seta/{}/'.format(seta.pk), {'name': 'seta_update'})
        self.assertEqual(response.status_code, 405)
        response_json = response.json()
        self.assertIn('detail', response_json)

    def test_delete(self):
        seta = Seta.objects.create(name="seta")
        response = self.client.delete('/api/seta/{}/'.format(seta.pk))
        self.assertEqual(response.status_code, 403)
        response_json = response.json()
        self.assertIn('detail', response_json)

    def test_delete_login(self):
        User.objects.create_superuser('admin', 'admin@test.com', 'admin')
        self.client.login(username='admin', password='admin')
        seta = Seta.objects.create(name="seta")
        response = self.client.delete('/api/seta/{}/'.format(seta.pk))
        self.assertEqual(response.status_code, 405)
        response_json = response.json()
        self.assertIn('detail', response_json)
