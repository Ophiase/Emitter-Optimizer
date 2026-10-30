# Flag hardcoded URLs on selected lines of a source file.
#
# -v file=<path>    name to print in the report
# -v added=<list>   comma-separated line numbers to report on, or ALL
#
# A line is spared only by a `hardcoded-url: <reason>` directive of three
# words or more, on the line itself or on the comment line right above it.

function is_added(number) { return added == "ALL" || (number in added_line) }

function is_justified(text) {
  return text ~ /hardcoded-url:[ \t]*[^ \t]+[ \t]+[^ \t]+[ \t]+[^ \t]+/
}

function is_url(text) {
  return text ~ /:\/\// || text ~ /scheme[ \t]*=[ \t]*["']/
}

function trimmed(text,   copy) {
  copy = text
  sub(/^[ \t]+/, "", copy)
  return copy
}

BEGIN {
  count = split(added, numbers, ",")
  for (index_ = 1; index_ <= count; index_++)
    if (numbers[index_] != "") added_line[numbers[index_] + 0] = 1
}

{
  if (is_added(NR) && is_url($0) && !is_justified($0) && !is_justified(previous)) {
    printf "%s:%d: %s\n", file, NR, trimmed($0)
    found++
  }
  previous = $0
}

END { exit (found > 0) ? 1 : 0 }
