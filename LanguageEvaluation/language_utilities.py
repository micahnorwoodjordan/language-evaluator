import copy


def titlize_map_entries(m, *args):
    """
    titleize only the provided part-of-speech configurations within the master LEMMA_OVERRIDE_CONFIGURATION
    :param m: dict
    :param args: list
    :return m: dict
    """
    m = copy.deepcopy(m)
    root_keys = list(m.keys())
    for root_key in root_keys:
        if root_key not in args:
            continue
        for child_key, child_value in zip(list(m[root_key].keys()), list(m[root_key].values())):
            m[root_key][child_key.title()] = child_value
    return m


class LanguageDetector:
    def __init__(self):
        pass

    def detect_language(self):
        pass
