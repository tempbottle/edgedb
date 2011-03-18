##
# Copyright (c) 2008-2010 Sprymix Inc.
# All rights reserved.
#
# See LICENSE for details.
##


from semantix.utils.lang import yaml
from semantix.utils.datastructures import StructMeta


class StructMeta(StructMeta):
    def get_yaml_validator_config(cls):
        result = {}

        for f, desc in cls._fields.items():
            field = {}

            types = cls.get_yaml_descriptors(desc.type)

            if len(types) == 1:
                field = types[0]
            else:
                field['type'] = 'choice'
                field['choice'] = types

            result[f] = field

        return result

    def get_yaml_descriptors(cls, types):
        result = []

        for type in types:
            field = {}

            if issubclass(type, yaml.Object):
                field['type'] = 'map'
                field['object'] = '%s.%s' % (type.__module__, type.__name__)

                if hasattr(type, 'get_yaml_validator_config'):
                    field['mapping'] = type.get_yaml_validator_config()
                else:
                    field['mapping'] = {'=': {'type': 'any'}}
            elif issubclass(type, bool):
                field = {'type': 'bool'}
            elif issubclass(type, int):
                field = {'type': 'int'}
            elif issubclass(type, str):
                field = {'type': 'str'}
            else:
                field = {'type': 'any'}

            result.append(field)

        return result

    def represent(cls, data):
        result = {}

        for f, desc in cls._fields.items():
            result[f] = getattr(data, f)

        return result

    @classmethod
    def adapt_value(mcls, field, value):
        """Tries to coerce the value into the type of the field"""

        if value is not None and not isinstance(value, field.type):
            adapter = yaml.ObjectMeta.get_adapter(field.type[0])
            if adapter:
                resolver = getattr(adapter, 'resolve', None)
                if resolver:
                    adapter = resolver(value)

                value = adapter(None, value)
                constructor = getattr(value, 'construct', None)
                if constructor:
                    constructor()
            else:
                value = field.adapt(value)
        return value