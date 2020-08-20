import ujson

from entitykb import Doc, Entity, fuzzy, Tokenizer, Normalizer, LabelSet
from entitykb.fuzzy import FuzzyIndex


def test_calculate_ratio(resolver, b_obama: Entity):
    ratio = resolver.calculate_ratio(b_obama, "Barak Obama")
    assert ratio > 90


def test_is_fuzzy_resolver_is_prefix(resolver, b_obama, m_obama):
    assert resolver.is_prefix("Barack")  # exact
    assert resolver.is_prefix("Michelle")  # exact
    assert resolver.is_prefix("Obama")  # exact
    assert resolver.is_prefix("Barak")  # deletion
    assert resolver.is_prefix("Obam")  # deletion
    assert resolver.is_prefix("Barakc")  # transpose
    assert resolver.is_prefix("Oabma")  # transpose
    assert resolver.is_prefix("Borack Hussain Oboma")  # replace
    assert resolver.is_prefix("Barrack Huussein Obamas")  # addition
    assert resolver.is_prefix("Barack,")  # conjunctions
    assert resolver.is_prefix("Barack or")  # conjunctions
    assert resolver.is_prefix("Barack and Michelle Obama")  # conjunctions


def test_find_candidates(
    index, b_obama: Entity, m_obama: Entity, michel_le: Entity
):
    all_labels = {"PRESIDENT", "FIRST_LADY", "SINGER"}
    assert {b_obama: 0, m_obama: 0} == index.find_candidates(
        "obama", all_labels
    )
    assert {b_obama: 1} == index.find_candidates("barak", all_labels)
    assert {m_obama: 1, michel_le: 1} == index.find_candidates(
        "michele", all_labels
    )
    assert {m_obama: 1} == index.find_candidates("michellle", all_labels)
    assert {michel_le: 0} == index.find_candidates("michel", all_labels)
    assert {} == index.find_candidates("barak", {"FIRST_LADY"})


def test_find(
    pipeline, resolver, b_obama: Entity, m_obama: Entity, michel_le: Entity,
):
    def do_run(text, *entities, label_set=None):
        doc: Doc = pipeline(text, label_set=label_set)
        expected = set(entity.key for entity in entities)
        found = set(doc_entity.entity_key for doc_entity in doc.entities)

        msg = ujson.dumps(doc.dict(), indent=4)
        assert expected == found, msg

    # exact matches
    do_run("Barack Obama", b_obama)
    do_run("Michelle Obama", m_obama)
    do_run("Michel'le", michel_le)

    # fuzzy matches
    do_run("Barak Obama", b_obama)
    do_run("Obama, Barak", b_obama)
    do_run("Barak and Micheale Obama", b_obama, m_obama)
    do_run("Barock & Michele Obama", b_obama, m_obama)
    do_run("Barak Hussien, Michelle Obama", b_obama, m_obama)
    do_run("Michel'le Obama", michel_le)
    do_run("Michel'le Denise Toussaint", michel_le)

    # insufficient ratios
    do_run("Obama")
    do_run("Barack")
    do_run("Michelle")

    # edge cases
    do_run("Barak and Michelle Obama, Barack", b_obama, m_obama)
    do_run("Barak, Michelle and Barack Obama", b_obama, m_obama)

    # labels
    do_run("Barack Obama", label_set=("FIRST_LADY",))
    do_run("Barak Obama", label_set=("FIRST_LADY",))
    do_run(
        "Barack and Michelle Obama",
        b_obama,
        m_obama,
        label_set=("PRESIDENT", "FIRST_LADY"),
    )

    # label_set will stop is_prefix from connecting
    do_run("Barack and Michelle Obama", label_set=("PRESIDENT",))


def test_fuzzy_prefix_with_labels(resolver, b_obama: Entity, m_obama: Entity):
    assert resolver.is_prefix("Barak", label_set=("PRESIDENT",))
    assert resolver.is_prefix("Obama", label_set=("PRESIDENT",))
    assert resolver.is_prefix("Obama", label_set=("FIRST_LADY",))
    assert not resolver.is_prefix("Barak", label_set=("FIRST_LADY",))
    assert not resolver.is_prefix("Michele", label_set=("PRESIDENT",))
    assert not resolver.is_prefix("Michelle", label_set=("PRESIDENT",))


def test_combinations(pipeline, b_obama: Entity, m_obama: Entity):
    combos = (
        "Barack, Michelle Obama",
        "Barack and Michelle Obama",
        "Barock & Michele Obama",
        "Barak Michele Obama",
        "Barack and Michelle Obama",
    )

    expected = tuple(entity.key for entity in (b_obama, m_obama))

    for combo in combos:
        doc = pipeline(combo)
        msg = ujson.dumps(doc.dict(), indent=4)

        found = tuple(doc_entity.entity_key for doc_entity in doc.entities)
        assert expected == found, f"{combo} => {found}"

        one = doc.entities[0]
        assert one.entity_key == b_obama.key
        assert 2 == len(one.tokens), msg
        assert 0 == one.offset, msg
        assert len(doc.tokens) - 1 == one.last_offset, msg

        two = doc.entities[1]
        assert two.entity_key == m_obama.key
        assert 2 == len(two.tokens), msg
        assert len(doc.tokens) - 2 == two.offset, msg
        assert len(doc.tokens) - 1 == two.last_offset, msg


class CompanyFuzzyIndex(FuzzyIndex):
    label_set = LabelSet.create("COMPANY")


def test_fuzzy(apple):
    index = CompanyFuzzyIndex.create(
        tokenizer=Tokenizer.create(),
        normalizer=Normalizer.create(),
        max_token_distance=1,
    )
    assert isinstance(index, fuzzy.FuzzyIndex)

    index.add(apple)
    index.add(Entity(name="banana", label="FRUIT"))

    # is_prefix
    assert index.is_prefix("aple")
    assert index.is_prefix("aple", label_set={"COMPANY", "ANOTHER"})
    assert index.is_prefix("inc")

    # conjunctions
    assert index.is_prefix("Apple and")
    assert index.is_prefix("apple,")

    # keys (2 names, 2 synonyms, 2 keys, map, and 7 edits)
    assert 11 == len(index.store.trie), str(list(index.store.trie.keys()))
