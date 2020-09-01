def generate_edits(token: str, max_token_distance: int):
    yield token, 0

    pairs = set()

    max_edit_distance = min(max_token_distance + 1, len(token) - 3)
    for edit_distance in range(1, max_edit_distance):
        for char_index in range(1, len(token) - edit_distance + 1):
            edit = token[:char_index] + token[char_index + edit_distance :]
            pair = edit, edit_distance
            if pair not in pairs:
                pairs.add(pair)
                yield pair
