import random
import string
import unittest
import uuid

import redis

import domain_model


def generate_string(n):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=n))


def generate_int(n):
    return random.randint(0, n)


def generate_float(n):
    return random.randint(0, n*1000)/1000


class DomainModelTestCase(unittest.TestCase):
    """
    Test Case class.
    """

    redis = redis.StrictRedis(decode_responses=True)

    def __init__(self, method_name='runTest'):
        super(DomainModelTestCase, self).__init__(method_name)
        self.domain_model = domain_model.DomainModel(self.redis)

    @classmethod
    def setUpClass(cls):

        # clear state
        cls.redis.flushdb()

    def test_1(self):

        t = 'test1'
        _id = str(uuid.uuid4())

        m1 = {
            _id: {
                'entity_id': _id,
                'name': generate_string(10),
                'age': str(generate_int(100)),
                'balance': str(generate_float(1000)),
                'friends': {str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())}
            }
        }

        for v in m1.values():
            self.domain_model.create(t, v)

        m2 = self.domain_model.retrieve(t)
        self.assertEqual(m1, m2)

    def test_2(self):

        t = 'test2'
        _id = str(uuid.uuid4())

        m1 = {
            _id: {
                'entity_id': _id,
                'name': generate_string(10),
                'age': str(generate_int(100)),
                'balance': str(generate_float(1000)),
                'friends': {str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())}
            }
        }

        for v in m1.values():
            self.domain_model.create(t, v)

        m1[_id]['age'] = str(generate_int(100))
        self.domain_model.update(t, m1[_id])

        m2 = self.domain_model.retrieve(t)
        self.assertEqual(m1, m2)

    def test_3(self):

        t = 'test3'
        _id = str(uuid.uuid4())

        m1 = {
            _id: {
                'entity_id': _id,
                'name': generate_string(10),
                'age': str(generate_int(100)),
                'balance': 0,
                'friends': {str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())},
            }
        }

        for v in m1.values():
            self.domain_model.create(t, v)

        self.domain_model.delete(t, m1[_id])

        m2 = self.domain_model.exists(t)
        self.assertIs(False, m2)
