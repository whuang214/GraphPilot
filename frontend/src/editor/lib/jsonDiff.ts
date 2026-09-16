// Minimal line-level diff (LCS) backing the JSON preview's git-style view.
// Pure and dependency-free, mirroring the small editor utilities
// (alignmentGuides.ts, resize.ts). Rows are tagged so the preview can
// render added / removed / context lines like a unified diff.

export type DiffRowType = 'add' | 'del' | 'context'

export interface DiffRow {
  type: DiffRowType
  text: string
}

export interface DiffStats {
  added: number
  removed: number
}

function toLines(text: string): string[] {
  // A truly empty string is "no lines"; split('\n') would otherwise yield [''].
  return text.length ? text.split('\n') : []
}

// Longest-common-subsequence line diff. O(n*m) time/space, which is fine for
// diagram JSON (hundreds of lines). The table holds LCS lengths of the two
// suffixes; walking it forward emits context where the sides agree and add/del
// where they diverge, preferring deletions on ties so output order is stable.
export function diffLines(before: string, after: string): DiffRow[] {
  const a = toLines(before)
  const b = toLines(after)
  const n = a.length
  const m = b.length

  // lcs[i][j] = length of the LCS of a[i:] and b[j:].
  const lcs: number[][] = Array.from({ length: n + 1 }, () => new Array<number>(m + 1).fill(0))
  for (let i = n - 1; i >= 0; i--) {
    for (let j = m - 1; j >= 0; j--) {
      lcs[i][j] = a[i] === b[j] ? lcs[i + 1][j + 1] + 1 : Math.max(lcs[i + 1][j], lcs[i][j + 1])
    }
  }

  const rows: DiffRow[] = []
  let i = 0
  let j = 0
  while (i < n && j < m) {
    if (a[i] === b[j]) {
      rows.push({ type: 'context', text: a[i] })
      i++
      j++
    } else if (lcs[i + 1][j] >= lcs[i][j + 1]) {
      rows.push({ type: 'del', text: a[i] })
      i++
    } else {
      rows.push({ type: 'add', text: b[j] })
      j++
    }
  }
  while (i < n) rows.push({ type: 'del', text: a[i++] })
  while (j < m) rows.push({ type: 'add', text: b[j++] })
  return rows
}

export function diffStats(rows: DiffRow[]): DiffStats {
  let added = 0
  let removed = 0
  for (const row of rows) {
    if (row.type === 'add') added++
    else if (row.type === 'del') removed++
  }
  return { added, removed }
}

// A "hunk" is a maximal run of changed (add/del) rows — used for prev/next change
// navigation and the scrollbar overview markers.
export interface DiffHunk {
  start: number
  end: number
}

export function diffHunks(rows: DiffRow[]): DiffHunk[] {
  const hunks: DiffHunk[] = []
  let i = 0
  while (i < rows.length) {
    if (rows[i].type === 'context') {
      i += 1
      continue
    }
    const start = i
    while (i < rows.length && rows[i].type !== 'context') i += 1
    hunks.push({ start, end: i })
  }
  return hunks
}

// Per-row old/new line numbers for the gutter: a context line advances both sides,
// a deletion only the old side, an addition only the new side.
export interface NumberedRow extends DiffRow {
  oldNo: number | null
  newNo: number | null
}

export function numberRows(rows: DiffRow[]): NumberedRow[] {
  let oldNo = 0
  let newNo = 0
  return rows.map((row) => {
    if (row.type === 'add') {
      newNo += 1
      return { ...row, oldNo: null, newNo }
    }
    if (row.type === 'del') {
      oldNo += 1
      return { ...row, oldNo, newNo: null }
    }
    oldNo += 1
    newNo += 1
    return { ...row, oldNo, newNo }
  })
}
