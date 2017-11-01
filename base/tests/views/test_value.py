# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
from base.models import Sensor, Seta, ValueSensorSeta, TYPE_INT


class ValueDeleteTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_superuser('admin', 'admin@test.com', 'admin')
        self.sensor = Sensor.objects.create(name="sensor")
        self.seta = Seta.objects.create(name="seta")
        self.seta.sensors.add(self.sensor)
        self.value = ValueSensorSeta.objects.create(seta=self.seta, sensor=self.sensor, value='value')

    def test_delete(self):
        response = self.client.delete('/api/value/{}/'.format(self.value.pk))
        self.assertEqual(response.status_code, 403)
        response_json = response.json()
        self.assertIn('detail', response_json)

    def test_delete_login(self):
        self.client.login(username='admin', password='admin')
        response = self.client.delete('/api/value/{}/'.format(self.value.pk))
        self.assertEqual(response.status_code, 405)
        response_json = response.json()
        self.assertIn('detail', response_json)


class ValueUpdateTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_superuser('admin', 'admin@test.com', 'admin')
        self.sensor = Sensor.objects.create(name="sensor")
        self.seta = Seta.objects.create(name="seta")
        self.seta.sensors.add(self.sensor)
        self.value = ValueSensorSeta.objects.create(seta=self.seta, sensor=self.sensor, value='value')

    def test_update(self):
        response = self.client.put('/api/value/{}/'.format(self.value.pk), {'value': 'new_val'})
        self.assertEqual(response.status_code, 403)
        response_json = response.json()
        self.assertIn('detail', response_json)

    def test_update_login(self):
        self.client.login(username='admin', password='admin')
        response = self.client.put('/api/value/{}/'.format(self.value.pk), {'value': 'new_val'})
        self.assertEqual(response.status_code, 405)
        response_json = response.json()
        self.assertIn('detail', response_json)


class ValueCreateTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_superuser('admin', 'admin@test.com', 'admin')
        self.sensor = Sensor.objects.create(name="sensor")
        self.seta = Seta.objects.create(name="seta")
        self.seta.sensors.add(self.sensor)

    def test_create(self):
        response = self.client.post('/api/value/', {
            'seta': self.seta,
            'sensor': self.sensor,
            'value': 'value'
        })
        self.assertEqual(response.status_code, 403)
        response_json = response.json()
        self.assertIn('detail', response_json)

    def test_create_login(self):
        self.client.login(username='admin', password='admin')
        response = self.client.post('/api/value/', {
            'seta.name': self.seta.name,
            'sensor.name': self.sensor.name,
            'value': 'value'
        })
        self.assertEqual(response.status_code, 201)
        response_json = response.json()
        self.assertIn('url', response_json)
        self.assertIn('sensor', response_json)
        self.assertIn('name', response_json['sensor'])
        self.assertEqual(response_json['sensor']['name'], self.sensor.name)
        self.assertIn('url', response_json['sensor'])
        self.assertIn('seta', response_json)
        self.assertIn('name', response_json['seta'])
        self.assertEqual(response_json['seta']['name'], self.seta.name)
        self.assertIn('url', response_json['seta'])
        self.assertIn('date', response_json)
        self.assertIn('value', response_json)
        self.assertEqual(response_json['value'], 'value')


class ValueCreateWithLoginTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_superuser('admin', 'admin@test.com', 'admin')
        self.client.login(username='admin', password='admin')
        self.sensor = Sensor.objects.create(name="sensor")
        self.seta = Seta.objects.create(name="seta")
        self.seta.sensors.add(self.sensor)

    def test_create_with_pk(self):
        response = self.client.post('/api/value/', {
            'seta.pk': self.seta.name,
            'sensor.pk': self.sensor.name,
            'value': 'value'
        })
        self.assertEqual(response.status_code, 400)
        response_json = response.json()
        self.assertIn('sensor', response_json)
        self.assertIn('name', response_json['sensor'])
        self.assertIn('seta', response_json)
        self.assertIn('name', response_json['seta'])

    def test_create_without_dot_name(self):
        response = self.client.post('/api/value/', {
            'seta': self.seta.name,
            'sensor': self.sensor.name,
            'value': 'value'
        })
        self.assertEqual(response.status_code, 400)
        response_json = response.json()
        self.assertIn('sensor', response_json)
        self.assertIn('seta', response_json)

    def test_create_wrong_sensor_data(self):
        self.sensor.sensor_type = TYPE_INT
        self.sensor.save()
        self.seta.check_value = True
        self.seta.save()

        response = self.client.post('/api/value/', {
            'seta.name': self.seta.name,
            'sensor.name': self.sensor.name,
            'value': 'value'
        })
        self.assertEqual(response.status_code, 400)
        response_json = response.json()
        self.assertIn('value', response_json)

    def test_create_seta_collision(self):
        Seta.objects.create(name=self.seta.name)
        response = self.client.post('/api/value/', {
            'seta.name': self.seta.name,
            'sensor.name': self.sensor.name,
            'value': 'value'
        })
        self.assertEqual(response.status_code, 400)
        response_json = response.json()
        self.assertIn('seta', response_json)
        self.assertEqual(response_json['seta'], 'Multiples options')

    def test_create_no_seta(self):
        response = self.client.post('/api/value/', {
            'seta.name': 'no exist',
            'sensor.name': self.sensor.name,
            'value': 'value'
        })
        self.assertEqual(response.status_code, 400)
        response_json = response.json()
        self.assertIn('seta', response_json)
        self.assertEqual(response_json['seta'], 'Not found')

    def test_create_sensor_collision(self):
        Sensor.objects.create(name=self.sensor.name)
        response = self.client.post('/api/value/', {
            'seta.name': self.seta.name,
            'sensor.name': self.sensor.name,
            'value': 'value'
        })
        self.assertEqual(response.status_code, 400)
        response_json = response.json()
        self.assertIn('sensor', response_json)
        self.assertEqual(response_json['sensor'], 'Multiples options')

    def test_create_no_sensor(self):
        response = self.client.post('/api/value/', {
            'seta.name': self.seta.name,
            'sensor.name': 'no exist',
            'value': 'value'
        })
        self.assertEqual(response.status_code, 400)
        response_json = response.json()
        self.assertIn('sensor', response_json)
        self.assertEqual(response_json['sensor'], 'Not found')

    def test_create_wrong_sensor(self):
        self.seta.sensors.remove(self.sensor)

        response = self.client.post('/api/value/', {
            'seta.name': self.seta.name,
            'sensor.name': self.sensor.name,
            'value': 'value'
        })
        self.assertEqual(response.status_code, 400)
        response_json = response.json()
        self.assertIn('seta', response_json)


class ValueListTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_superuser('admin', 'admin@test.com', 'admin')
        self.sensor = Sensor.objects.create(name="sensor")
        self.seta = Seta.objects.create(name="seta")
        self.seta.sensors.add(self.sensor)

    def test_list_no_login(self):
        response = self.client.get('/api/value/')
        self.assertEqual(response.status_code, 403)
        response_json = response.json()
        self.assertIn('detail', response_json)

    def test_list_empty(self):
        self.client.login(username='admin', password='admin')
        response = self.client.get('/api/value/')
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
        self.client.login(username='admin', password='admin')
        value = ValueSensorSeta.objects.create(seta=self.seta, sensor=self.sensor, value='value')
        response = self.client.get('/api/value/')
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
        self.assertIn('date', result)
        self.assertIn('sensor', result)
        self.assertIn('name', result['sensor'])
        self.assertEqual(result['sensor']['name'], value.sensor.name)
        self.assertIn('seta', result)
        self.assertIn('name', result['seta'])
        self.assertEqual(result['seta']['name'], value.seta.name)
        self.assertIn('value', result)
        self.assertEqual('value', value.value)
        self.assertIn('url', result)
