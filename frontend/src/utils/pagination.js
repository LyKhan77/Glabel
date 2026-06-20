export function paginateItems(items, page, pageSize) {
  const total = items.length
  const pageCount = Math.max(1, Math.ceil(total / pageSize))
  const currentPage = Math.min(Math.max(1, page), pageCount)
  const startIndex = (currentPage - 1) * pageSize
  const endIndex = Math.min(startIndex + pageSize, total)

  return {
    items: items.slice(startIndex, endIndex),
    page: currentPage,
    pageCount,
    start: total ? startIndex + 1 : 0,
    end: endIndex,
    total
  }
}
