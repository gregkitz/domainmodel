def is_key(_value):
    """
    Check if a value is a key, i.e. has to be looked up on Redis root level.

    :param _value: The string to be checked.
    :return: True if the given value is a Redis key, false otherwise.
    """
    return '_' in _value and ':' in _value


class DomainModel(object):
    """
    Domain Model class.

    It persists Python dictionaries with an 'entity_id' to Redis Hashes, Lists and Sets.
    Currently only 1 level of nesting is supported.
    """
    redis = None

    def __init__(self, _redis):
        """
        :param _redis: A redis instance.
        """
        self.redis = _redis

    def create(self, _topic, _values):
        """
        Set an entity.

        :param _topic: The type of entity.
        :param _values: The entity properties.
        """
        self.redis.sadd('{}_ids'.format(_topic), _values['entity_id'])
        for k, v in _values.items():
            if isinstance(v, list):
                lid = '{}_{}:{}'.format(_topic, k, _values['entity_id'])
                self.redis.hset('{}_entity:{}'.format(_topic, _values['entity_id']), k, lid)
                self.redis.rpush(lid, *v)
            elif isinstance(v, set):
                sid = '{}_{}:{}'.format(_topic, k, _values['entity_id'])
                self.redis.hset('{}_entity:{}'.format(_topic, _values['entity_id']), k, sid)
                self.redis.sadd(sid, *v)
            elif isinstance(v, dict):
                did = '{}_{}:{}'.format(_topic, k, _values['entity_id'])
                self.redis.hset('{}_entity:{}'.format(_topic, _values['entity_id']), k, did)
                self.redis.hmset(did, v)
            else:
                self.redis.hset('{}_entity:{}'.format(_topic, _values['entity_id']), k, v)

    def retrieve(self, _topic):
        """
        Get an entity.

        :param _topic: The type of entity.
        :return: A dict with the entity properties.
        """
        result = {}
        for eid in self.redis.smembers('{}_ids'.format(_topic)):
            result[eid] = self.redis.hgetall('{}_entity:{}'.format(_topic, eid))
            for k, v in result[eid].items():
                if is_key(v):
                    rtype = self.redis.type(v)
                    if rtype == 'list':
                        result[eid][k] = self.redis.lrange(v, 0, -1)
                    elif rtype == 'set':
                        result[eid][k] = self.redis.smembers(v)
                    elif rtype == 'hash':
                        result[eid][k] = self.redis.hgetall(v)
                    else:
                        result[eid][k] = self.redis.hget(v)
        return result

    def update(self, _topic, _values):
        """
        Delete and set an entity.

        :param _topic: The type of entity.
        :param _values: The entity properties.
        """
        for k, v in _values.items():
            if isinstance(v, list):
                lid = '{}_{}:{}'.format(_topic, k, _values['entity_id'])
                self.redis.hset('{}_entity:{}'.format(_topic, _values['entity_id']), k, lid)
                self.redis.delete(lid)
                self.redis.rpush(lid, *v)
            elif isinstance(v, set):
                sid = '{}_{}:{}'.format(_topic, k, _values['entity_id'])
                self.redis.hset('{}_entity:{}'.format(_topic, _values['entity_id']), k, sid)
                self.redis.delete(sid)
                self.redis.sadd(sid, *v)
            elif isinstance(v, dict):
                did = '{}_{}:{}'.format(_topic, k, _values['entity_id'])
                self.redis.hset('{}_entity:{}'.format(_topic, _values['entity_id']), k, did)
                self.redis.delete(did)
                self.redis.hmset(did, *v)
            else:
                self.redis.hset('{}_entity:{}'.format(_topic, _values['entity_id']), k, v)

    def delete(self, _topic, _values):
        """
        Delete an entity.

        :param _topic: The type of entity.
        :param _values: The entity properties.
        """
        self.redis.srem('{}_ids'.format(_topic), 1, _values['entity_id'])
        self.redis.delete('{}_entity:{}'.format(_topic, _values['entity_id']))
        for k, v in _values.items():
            if isinstance(v, (list, set, dict)):
                self.redis.delete('{}_{}:{}'.format(_topic, k, _values['entity_id']))

    def exists(self, _topic, _id=None):
        """
        Check if an entity exists.

        :param _topic: The type of entity.
        :param _id: An optional entity ID.
        :return: True iff an entity exists, False otherwise.
        """
        if self.redis.exists('{}_ids'.format(_topic)):
            return True if not _id else self.redis.sismember('{}_ids'.format(_topic), _id)
        return False
