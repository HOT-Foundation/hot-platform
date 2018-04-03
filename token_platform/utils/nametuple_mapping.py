import collections


def map_namedtuple(data):
    if(isinstance(data, dict)):
        for key in data.keys():
            data[key] = map_namedtuple(data[key])
        return namedtuple_from_mapping(data)
    if(isinstance(data, list)):
        for i in range(len(data)):
            data[i] = namedtuple_from_mapping(data[i])
    return data


def namedtuple_from_mapping(mapping, name="Tupperware"):
    this_namedtuple_maker = collections.namedtuple(name, mapping.keys())
    return this_namedtuple_maker(**mapping)