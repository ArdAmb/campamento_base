# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from django.test import TestCase

from base.models import (
    Sensor,
    Seta,
    ValueSensorSeta,
    TYPE_INT,
    TYPE_FLOAT,
    TYPE_STRING
)


class SensorTestCase(TestCase):
    def test_duplicate_name(self):
        Sensor.objects.create(name="sensor")
        Sensor.objects.create(name="sensor")
        self.assertEqual(Sensor.objects.filter(name="sensor").count(), 2)

    def test_duplicate_name_different_types(self):
        Sensor.objects.create(name="sensor", sensor_type=TYPE_STRING)
        Sensor.objects.create(name="sensor", sensor_type=TYPE_FLOAT)
        Sensor.objects.create(name="sensor", sensor_type=TYPE_INT)
        self.assertEqual(Sensor.objects.filter(name="sensor").count(), 3)


class SetaTestCase(TestCase):
    def test_duplicate_name(self):
        Seta.objects.create(name="seta")
        Seta.objects.create(name="seta")
        self.assertEqual(Seta.objects.filter(name="seta").count(), 2)


class ValueSensorSetaTestCase(TestCase):
    def setUp(self):
        self.seta = Seta.objects.create(name="seta")

    def test_string_sensor(self):
        sensor = Sensor.objects.create(name="str", sensor_type=TYPE_STRING)
        self.seta.sensors.add(sensor)
        real_value = 'string'
        value = ValueSensorSeta.objects.create(seta=self.seta, sensor=sensor, value=real_value)
        value = ValueSensorSeta.objects.get(pk=value.pk)
        self.assertEqual(value.get_value(), real_value)
        self.assertEqual(value.value, str(real_value))
        self.assertEqual(str(value), str(real_value))

    def test_float_sensor(self):
        sensor = Sensor.objects.create(name="float", sensor_type=TYPE_FLOAT)
        self.seta.sensors.add(sensor)
        real_value = 1.05
        value = ValueSensorSeta.objects.create(seta=self.seta, sensor=sensor, value=real_value)
        value = ValueSensorSeta.objects.get(pk=value.pk)
        self.assertEqual(value.get_value(), real_value)
        self.assertEqual(value.value, str(real_value))

    def test_invalid_float_sensor(self):
        sensor = Sensor.objects.create(name="float", sensor_type=TYPE_FLOAT)
        self.seta.sensors.add(sensor)
        real_value = 'string'
        value = ValueSensorSeta.objects.create(seta=self.seta, sensor=sensor, value=real_value)
        value = ValueSensorSeta.objects.get(pk=value.pk)
        self.assertEqual(value.value, real_value)
        self.assertRaises(ValueError, value.get_value)

    def test_int_sensor(self):
        sensor = Sensor.objects.create(name="int", sensor_type=TYPE_INT)
        self.seta.sensors.add(sensor)
        real_value = 1
        value = ValueSensorSeta.objects.create(seta=self.seta, sensor=sensor, value=real_value)
        value = ValueSensorSeta.objects.get(pk=value.pk)
        self.assertEqual(value.get_value(), real_value)
        self.assertEqual(value.value, str(real_value))

    def test_invalid_int_sensor_with_string(self):
        sensor = Sensor.objects.create(name="int", sensor_type=TYPE_INT)
        self.seta.sensors.add(sensor)
        real_value = 'string'
        value = ValueSensorSeta.objects.create(seta=self.seta, sensor=sensor, value=real_value)
        value = ValueSensorSeta.objects.get(pk=value.pk)
        self.assertEqual(value.value, real_value)
        self.assertRaises(ValueError, value.get_value)

    def test_invalid_int_sensor_with_float(self):
        sensor = Sensor.objects.create(name="int", sensor_type=TYPE_INT)
        self.seta.sensors.add(sensor)
        real_value = 1.05
        value = ValueSensorSeta.objects.create(seta=self.seta, sensor=sensor, value=real_value)
        value = ValueSensorSeta.objects.get(pk=value.pk)
        self.assertEqual(value.value, str(real_value))
        self.assertRaises(ValueError, value.get_value)

    def test_clean_float_with_string(self):
        sensor = Sensor.objects.create(name="float", sensor_type=TYPE_FLOAT)
        self.seta.sensors.add(sensor)
        real_value = 'string'
        value = ValueSensorSeta.objects.create(seta=self.seta, sensor=sensor, value=real_value)
        self.assertRaisesMessage(ValidationError, 'string is not a float', value.clean)

    def test_clean_int_with_string(self):
        sensor = Sensor.objects.create(name="int", sensor_type=TYPE_INT)
        self.seta.sensors.add(sensor)
        real_value = 'string'
        value = ValueSensorSeta.objects.create(seta=self.seta, sensor=sensor, value=real_value)
        self.assertRaisesMessage(ValidationError, 'string is not a integer', value.clean)

    def test_clean_int_with_float_as_string(self):
        sensor = Sensor.objects.create(name="int", sensor_type=TYPE_INT)
        self.seta.sensors.add(sensor)
        real_value = '1.05'
        value = ValueSensorSeta.objects.create(seta=self.seta, sensor=sensor, value=real_value)
        self.assertRaisesMessage(ValidationError, '1.05 is not a integer', value.clean)

    def test_clean_int_with_float(self):
        sensor = Sensor.objects.create(name="int", sensor_type=TYPE_INT)
        self.seta.sensors.add(sensor)
        real_value = 1.05
        value = ValueSensorSeta.objects.create(seta=self.seta, sensor=sensor, value=real_value)
        self.assertEqual(value.clean(), 1)
        self.assertEqual(value.get_value(), 1)
        value = ValueSensorSeta.objects.get(pk=value.pk)
        self.assertRaisesMessage(ValidationError, '1.05 is not a integer', value.clean)

    def test_clean_no_sensor(self):
        sensor = Sensor.objects.create(name="sensor")
        value = ValueSensorSeta.objects.create(seta=self.seta, sensor=sensor, value='value')
        self.assertRaisesMessage(ValidationError, 'sensor is not valid for seta', value.clean)
        self.assertEqual(value.get_value(), 'value')
        value = ValueSensorSeta.objects.get(pk=value.pk)
        self.assertRaisesMessage(ValidationError, 'sensor is not valid for seta', value.clean)
        self.assertEqual(value.get_value(), 'value')
