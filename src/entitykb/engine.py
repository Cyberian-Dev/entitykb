from dataclasses import dataclass

import entitykb


@dataclass
class Engine(object):
    index: entitykb.Index = None
