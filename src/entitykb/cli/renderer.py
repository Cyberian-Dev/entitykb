from typing import List, Dict
import tabulate
import ujson


from entitykb import Doc


def render_doc(doc: Doc, output_fmt: str = "table"):
    method = globals().get("render_" + output_fmt)

    if not method:
        raise NotImplementedError("Format method not found: " + output_fmt)

    return method(doc)


def render_json(doc: Doc):
    return ujson.dumps(doc.dict(), indent=4)


def render_jsonl(doc: Doc):
    for value in iter_values(doc, is_table=False):
        line = ujson.dumps(value)
        yield line
        yield "\n"


def render_table(doc: Doc):
    values = list(iter_values(doc, is_table=True))

    if values:
        output = tabulate.tabulate(
            values, headers="keys", tablefmt="pretty", colalign=("left",) * 3,
        )
    else:
        output = "No entities found."

    return output


def iter_values(doc: Doc, is_table: bool) -> List[Dict]:
    for doc_ent in doc.entities:

        if is_table:
            # meta_items = (doc_ent.meta or {}).items()
            record = {
                "text": doc_ent.text,
                "tokens": ", ".join(
                    map(lambda t: str(t.offset), doc_ent.tokens)
                ),
                "key": doc_ent.entity_key,
                # "name": doc_ent.name,
                # "meta": "\n".join(map(lambda k: ": ".join(k), meta_items)),
                # "synonyms": "\n".join(doc_ent.entity.synonyms),
            }
        else:
            record = doc_ent.dict()

        yield record
