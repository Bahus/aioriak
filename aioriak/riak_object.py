from riak.content import RiakContent
from riak.riak_object import content_property


class RiakObject:
    '''
    The RiakObject holds meta information about a Riak object, plus the
    object's data.
    '''
    siblings = []

    def __init__(self, client, bucket, key=None):
        '''
        Construct a new RiakObject.
        :param client: A RiakClient object.
        :type client: :class:`RiakClient <aioriak.client.RiakClient>`
        :param bucket: A RiakBucket object.
        :type bucket: :class:`RiakBucket <aioriak.bucket.RiakBucket>`
        :param key: An optional key. If not specified, then the key
         is generated by the server when :func:`store` is called.
        :type key: string
        '''

        if key is not None and len(key) == 0:
            raise ValueError('Key name must either be "None"'
                             ' or a non-empty string.')
        self.client = client
        self.bucket = bucket
        self.key = key
        self.siblings = [RiakContent(self)]
        self._resolver = None

    async def reload(self):
        '''
        Reload the object from Riak. When this operation completes, the
        object could contain new metadata and a new value, if the object
        was updated in Riak since it was last retrieved.
        .. note:: Even if the key is not found in Riak, this will
           return a :class:`RiakObject`. Check the :attr:`exists`
           property to see if the key was found.
        :rtype: :class:`RiakObject`
        '''

        await self.client.get(self)
        return self

    data = content_property('data', doc='''
        The data stored in this object, as Python objects. For the raw
        data, use the `encoded_data` property. If unset, accessing
        this property will result in decoding the `encoded_data`
        property into Python values. The decoding is dependent on the
        `content_type` property and the bucket's registered decoders.
        ''')

    encoded_data = content_property('encoded_data', doc='''
        The raw data stored in this object, essentially the encoded
        form of the `data` property. If unset, accessing this property
        will result in encoding the `data` property into a string. The
        encoding is dependent on the `content_type` property and the
        bucket's registered encoders.
        ''')

    def _get_resolver(self):
        if callable(self._resolver):
            return self._resolver
        elif self._resolver is None:
            return self.bucket.resolver
        else:
            raise TypeError("resolver is not a function")

    def _set_resolver(self, value):
        if value is None or callable(value):
            self._resolver = value
        else:
            raise TypeError("resolver is not a function")

    resolver = property(_get_resolver, _set_resolver,
                        doc='''The sibling-resolution function for this
                        object. If the resolver is not set, the
                        bucket's resolver will be used.''')