from typing import List

from entitykb import RegexResolver, Entity
from .model import Email


class EmailResolver(RegexResolver):
    allowed_labels = {Email.get_default_label()}
    re_tokens = [
        r"[a-zA-Z0-9_.+-]+",
        r"@",
        r"[a-zA-Z0-9-]+",
        r"\.",
        r"[a-zA-Z0-9-]+",
        r"(?:\.[a-zA-Z0-9-]+)*",
    ]

    def create_entities(self, term: str, re_match) -> List[Entity]:
        groups = re_match.groups()
        domain = "".join(groups[2:])
        username = groups[0]
        entity = Email(name=term, username=username, domain=domain)
        return [entity]
