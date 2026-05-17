from typing import Any

DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


def clamp_page(page: int) -> int:
    return max(1, page)


def clamp_page_size(page_size: int) -> int:
    return max(1, min(page_size, MAX_PAGE_SIZE))


async def paginate(query: Any, page: int, page_size: int) -> dict[str, Any]:
    page = clamp_page(page)
    page_size = clamp_page_size(page_size)
    total = await query.count()
    items = await query.skip((page - 1) * page_size).limit(page_size).to_list()
    return {"items": items, "total": total, "page": page, "page_size": page_size}
