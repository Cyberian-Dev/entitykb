import time
from typing import List, Optional

from . import Config, Pipeline, Entity, LabelSet


class KB(object):
    def __init__(self, config: Config):
        start_time = time.time()
        self.config = config
        self.pipeline = Pipeline.create(config)
        self.load_time = time.time() - start_time
        self.is_dirty = False

    @classmethod
    def create(cls, root_dir: str = None):
        config = Config.create(root_dir)
        kb = cls(config=config)
        return kb

    def __call__(self, text: str, label_set: LabelSet = None):
        return self.process(text, label_set)

    @property
    def index(self):
        return self.pipeline.index

    def __len__(self):
        return len(self.pipeline)

    def reload(self):
        self.pipeline.reload()

    def reset(self):
        self.pipeline.reset()

    def add(self, *entities):
        self.is_dirty = True
        self.pipeline.add(*entities)

    def commit(self):
        self.pipeline.commit()
        self.is_dirty = False

    def find(self, text: str, label_set: LabelSet = None) -> List[Entity]:
        doc = self.process(text, label_set=label_set)
        return [doc_ent.entity for doc_ent in doc.entities]

    def find_one(
        self, text: str, label_set: LabelSet = None
    ) -> Optional[Entity]:
        entities = self.find(text, label_set=label_set)
        if entities:
            return entities[0]

    def info(self):
        return {
            "config": self.config.info(),
            "index": self.index.info(),
            "load_time": f"{self.load_time :.2} sec",
            "is_dirty": self.is_dirty,
        }

    def process(self, text: str, label_set: LabelSet = None):
        return self.pipeline(text=text, label_set=label_set)

    def suggest(
        self, term: str, label_set: LabelSet, limit: int = None
    ) -> List[str]:
        results = self.index.suggest(term, label_set=label_set, limit=limit)
        return results


def load(root_dir: str = None):
    kb = KB.create(root_dir=root_dir)
    return kb
