# Usage: awk -v file=<path> -v added=<lines|ALL> -f markdown-smell.awk <file>
# Prints one finding per smell on a block that holds an added line: a long
# paragraph or list item, an ASCII drawing in a code block, a mermaid block a
# renderer will not draw. File length is judged by markdown-smell.sh.

BEGIN {
  PARAGRAPH_MAX = 3
  ITEM_MAX = 4
  count = split(added, numbers, ",")
  for (position = 1; position <= count; position++) wanted[numbers[position]] = 1
}

function is_added(line) {
  return added == "ALL" || (line in wanted)
}

function report(line, smell, message) {
  printf "%s:%d: [%s] %s\n", file, line, smell, message
}

function close_block() {
  if (block_kind == "paragraph" && block_length > PARAGRAPH_MAX && block_added)
    report(block_start, "PARAGRAPH", block_length " lines; split it, or make it bullets")
  if (block_kind == "item" && block_length > ITEM_MAX && block_added)
    report(block_start, "PARAGRAPH", "a list item of " block_length " lines; one idea per bullet")
  block_kind = ""
  block_length = 0
  block_added = 0
}

function open_block(kind) {
  close_block()
  block_kind = kind
  block_start = FNR
}

function extend_block() {
  block_length++
  if (is_added(FNR)) block_added = 1
}

FNR == 1 && /^---[ \t]*$/ { in_front_matter = 1; next }
in_front_matter { if (/^---[ \t]*$/) in_front_matter = 0; next }

/^[ \t]*(```|~~~)/ {
  if (!in_fence) {
    close_block()
    in_fence = 1
    fence_start = FNR
    fence_language = $0
    sub(/^[ \t]*(```|~~~)[ \t]*/, "", fence_language)
    fence_ascii = 0
    fence_mermaid_issue = ""
    fence_added = 0
    graph_direction = ""
    delete out_degree
    delete edges
    next
  }
  in_fence = 0
  if (fence_language == "mermaid") judge_layout()
  if (fence_added && fence_ascii)
    report(fence_start, "ASCII", "a drawing in a code block; draw it as a mermaid diagram")
  if (fence_added && fence_mermaid_issue != "")
    report(fence_start, "MERMAID", fence_mermaid_issue)
  next
}

function record_edge(text,    source, target) {
  if (!match(text, /^[ \t]*[A-Za-z0-9_]+/)) return
  source = substr(text, RSTART, RLENGTH)
  gsub(/[ \t]/, "", source)
  sub(/^[^-=.]*(-->|---|-\.->|==>)[ \t]*(\|[^|]*\|)?[ \t]*/, "", text)
  if (!match(text, /^[A-Za-z0-9_]+/)) return
  target = substr(text, RSTART, RLENGTH)
  out_degree[source]++
  edges[source] = edges[source] " " target
}

function chain_length(node, visiting,    children, count, position, longest, length_here) {
  if (node in visiting) return 0
  visiting[node] = 1
  longest = 0
  count = split(edges[node], children, " ")
  for (position = 1; position <= count; position++) {
    length_here = 1 + chain_length(children[position], visiting)
    if (length_here > longest) longest = length_here
  }
  delete visiting[node]
  return longest
}

function judge_layout(    node, widest, longest, visiting) {
  widest = 0
  for (node in out_degree) if (out_degree[node] > widest) widest = out_degree[node]
  if (graph_direction ~ /^(TD|TB|BT)$/ && widest > 4)
    fence_mermaid_issue = widest " branches side by side; write graph LR so they stack"
  if (graph_direction ~ /^(LR|RL)$/) {
    longest = 0
    for (node in edges) {
      delete visiting
      if (chain_length(node, visiting) > longest) longest = chain_length(node, visiting)
    }
    if (longest > 4)
      fence_mermaid_issue = "a chain of " longest + 1 " nodes runs to the right; write graph TD"
  }
}

in_fence {
  if (is_added(FNR)) fence_added = 1
  if (fence_language != "mermaid" && $0 ~ /─|│|┌|┐|└|┘|├|┤|┬|┴|┼|▶|◀|▼|▲|►|◄/) fence_ascii = 1
  if (fence_language != "mermaid") next
  if (graph_direction == "" && match($0, /^[ \t]*graph[ \t]+[A-Z]+/)) {
    graph_direction = $0
    sub(/^[ \t]*graph[ \t]+/, "", graph_direction)
    sub(/[ \t].*$/, "", graph_direction)
  }
  if ($0 ~ /-->|---|-\.->|==>/) record_edge($0)
  if ($0 ~ /^[ \t]*flowchart([ \t]|$)/)
    fence_mermaid_issue = "flowchart is not drawn everywhere; write graph"
  if ($0 ~ /---->/)
    fence_mermaid_issue = "the ----> long arrow is not drawn everywhere; write -->"
  next
}

/^[ \t]*$/ { close_block(); next }
/^[ \t]*(#|\||>|<|!\[|\[!\[)/ { close_block(); next }
/^[ \t]*([-*+]|[0-9]+[.)])[ \t]/ { open_block("item"); extend_block(); next }
block_kind == "" { open_block("paragraph") }
{ extend_block() }

END {
  close_block()
}
