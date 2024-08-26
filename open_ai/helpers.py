from open_ai.config import Config


def rows_to_remove_in_model(model: list[dict[str, str]]) -> int:
    content_size_list = []
    overall_content_size = 0
    for line in model:
        content_size = len(line['content'])
        content_size_list.append(content_size)
        overall_content_size += content_size

    size_diff = overall_content_size - Config.read('TOKENS_PER_CONVERSATION')
    rows_to_remove = 0
    for content_size in content_size_list:
        if size_diff > 0:
            size_diff - content_size
            rows_to_remove += 1
        else:
            break

    return rows_to_remove


def remove_rows_from_model(model: list[dict[str, str]], rows: int):
    for i in range(rows):
        if rows == 0:
            break
        model.pop(1)
        rows -= 1
