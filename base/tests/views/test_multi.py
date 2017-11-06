# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from django.contrib.auth.models import User
from base.models import Sensor, Seta, ValueSensorSeta
from django.test import Client


class MultiValueCreateTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_superuser('admin', 'admin@test.com', 'admin')
        self.sensor = Sensor.objects.create(name="sensor")
        self.sensor_extra = Sensor.objects.create(name="sensor_extra")
        self.sensor_not_used = Sensor.objects.create(name="sensor_not_used")
        self.seta = Seta.objects.create(name="seta")
        self.seta.sensors.add(self.sensor)
        self.seta.sensors.add(self.sensor_extra)

    def test_create(self):
        with self.settings(LOCAL_NETWORK='192.168.0.0/24'):
            query = ValueSensorSeta.objects.filter(seta=self.seta, sensor=self.sensor, value='value')
            self.assertEqual(query.count(), 0)
            response = self.client.post('/api/multi/{}/'.format(self.seta.pk), {
                self.sensor.name: 'value'
            })
            self.assertEqual(response.status_code, 403)
            response_json = response.json()
            self.assertIn('detail', response_json)

    def test_create_one_login(self):
        self.client.login(username='admin', password='admin')
        query = ValueSensorSeta.objects.filter(seta=self.seta, sensor=self.sensor, value='value')
        self.assertEqual(query.count(), 0)
        response = self.client.post('/api/multi/{}/'.format(self.seta.pk), {
            self.sensor.name: 'value'
        })
        self.assertEqual(response.status_code, 201)
        response_json = response.json()
        self.assertIn('errors', response_json)
        self.assertEqual(len(response_json['errors']), 0)
        self.assertIn('created', response_json)
        self.assertEqual(len(response_json['created']), 1)
        created = response_json['created'][0]
        self.assertIn('url', created)
        self.assertIn('date', created)
        self.assertIn('sensor', created)
        self.assertIn('name', created['sensor'])
        self.assertEqual(created['sensor']['name'], self.sensor.name)
        self.assertIn('seta', created)
        self.assertIn('name', created['seta'])
        self.assertEqual(created['seta']['name'], self.seta.name)
        self.assertIn('value', created)
        self.assertEqual(created['value'], 'value')
        self.assertEqual(query.count(), 1)

    def test_create_multiple(self):
        self.client.login(username='admin', password='admin')
        query = ValueSensorSeta.objects.filter(seta=self.seta, value='value')
        self.assertEqual(query.count(), 0)
        response = self.client.post('/api/multi/{}/'.format(self.seta.pk), {
            self.sensor.name: 'value',
            self.sensor_extra.name: 'value'
        })
        self.assertEqual(response.status_code, 201)
        response_json = response.json()
        self.assertIn('errors', response_json)
        self.assertEqual(len(response_json['errors']), 0)
        self.assertIn('created', response_json)
        self.assertEqual(len(response_json['created']), 2)

        for created in response_json['created']:
            self.assertIn('url', created)
            self.assertIn('date', created)
            self.assertIn('sensor', created)
            self.assertIn('name', created['sensor'])
            self.assertIn(
                created['sensor']['name'],
                [self.sensor.name, self.sensor_extra.name]
            )
            self.assertIn('seta', created)
            self.assertIn('name', created['seta'])
            self.assertEqual(created['seta']['name'], self.seta.name)
            self.assertIn('value', created)
            self.assertEqual(created['value'], 'value')
        self.assertEqual(query.count(), 2)

    def test_wrong_seta(self):
        self.client.login(username='admin', password='admin')
        response = self.client.post('/api/multi/0/', {
            self.sensor.name: 'value'
        })
        self.assertEqual(response.status_code, 404)

    def test_wrong_sensor(self):
        self.client.login(username='admin', password='admin')
        response = self.client.post('/api/multi/{}/'.format(self.seta.pk), {
            self.sensor_not_used.name: 'value'
        })
        self.assertEqual(response.status_code, 400)
        response_json = response.json()
        self.assertIn('errors', response_json)
        self.assertEqual(len(response_json['errors']), 1)
        self.assertIn(self.sensor_not_used.name, response_json['errors'])
        self.assertEqual(response_json['errors'][self.sensor_not_used.name], 'Not found')
        self.assertIn('created', response_json)
        self.assertEqual(len(response_json['created']), 0)

    def test_multi_name_sensor(self):
        self.client.login(username='admin', password='admin')
        sensor = Sensor.objects.create(name=self.sensor.name)
        self.seta.sensors.add(sensor)
        response = self.client.post('/api/multi/{}/'.format(self.seta.pk), {
            self.sensor.name: 'value'
        })
        self.assertEqual(response.status_code, 400)
        response_json = response.json()
        self.assertIn('errors', response_json)
        self.assertEqual(len(response_json['errors']), 1)
        self.assertIn(self.sensor.name, response_json['errors'])
        self.assertEqual(response_json['errors'][self.sensor.name], 'Multiples options')
