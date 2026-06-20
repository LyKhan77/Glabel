import assert from 'node:assert/strict'
import { test } from 'node:test'

import { paginateItems } from '../src/utils/pagination.js'

test('paginates items and clamps invalid pages', () => {
  const items = Array.from({ length: 55 }, (_, index) => index + 1)

  assert.deepEqual(paginateItems(items, 1, 50), {
    items: items.slice(0, 50),
    page: 1,
    pageCount: 2,
    start: 1,
    end: 50,
    total: 55
  })

  assert.deepEqual(paginateItems(items, 99, 50), {
    items: items.slice(50),
    page: 2,
    pageCount: 2,
    start: 51,
    end: 55,
    total: 55
  })
})

test('returns empty pagination metadata for empty lists', () => {
  assert.deepEqual(paginateItems([], 1, 50), {
    items: [],
    page: 1,
    pageCount: 1,
    start: 0,
    end: 0,
    total: 0
  })
})
