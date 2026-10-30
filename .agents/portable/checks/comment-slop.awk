# Flag comment slop on selected lines of a source file.
#
# -v file=<path>    name to print in the report
# -v added=<list>   comma-separated line numbers to report on, or ALL
# -v syntax=<name>  python (default), yaml, just, shell, javascript or rust
#
# The shapes, and which of them each syntax answers for, are in
# ../rules/comments.md.

function is_blank(text) { return text ~ /^[ \t]*$/ }

function is_comment(text) {
  if (doc_comments_are_code && text ~ /^[ \t]*\/\/[\/!]/)
    return 0
  if (comment_is_slash)
    return text ~ /^[ \t]*(\/\/|\/\*|\*)/
  return text ~ /^[ \t]*#/
}

function is_exempt(text) {
  return text ~ /^#!/ \
      || text ~ /coding[:=]/ \
      || text ~ /^[ \t]*(#|\/\/)[ \t]*(noqa|type:|pragma|hardcoded-url:|pylint|ruff|fmt:|isort:|mypy:|nosec|NOSONAR|shellcheck|eslint|biome-ignore|djlint|prettier|yamllint|yaml-language-server|jshint|globals|region|endregion)/
}

function is_assignment(text) { return text ~ assignment_pattern }

# A comment that names another file, or a symbol this one never touches, is
# describing coupling the code itself does not carry. Reports the first such
# name only. Deliberately narrow: a domain word the file happens not to spell
# is not a design problem, a neighbour's filename is.
function scan_remote(number, text,   rest, candidate) {
  rest = text
  sub(/^[ \t]*(#|\/\/|\*)[ \t!]*/, "", rest)
  if (rest ~ /https?:\/\//) return
  while (match(rest, /[A-Za-z0-9_.\/-]+\.(py|ya?ml|sh|js|md|json|toml|just|sql|html|awk)\y|[A-Za-z_][A-Za-z0-9]*_[A-Za-z0-9_]*(\.[A-Za-z0-9_]+)+|[A-Z][a-z]+[A-Z][A-Za-z0-9]*/)) {
    candidate = substr(rest, RSTART, RLENGTH)
    rest = substr(rest, RSTART + RLENGTH)
    if (index(code_text, candidate) == 0) {
      report(number, "REMOTE", text)
      return
    }
  }
}

function description_length(text,   value) {
  if (!match(text, /description[ \t]*=[ \t]*"[^"]*"/)) return 0
  value = substr(text, RSTART, RLENGTH)
  sub(/^description[ \t]*=[ \t]*"/, "", value)
  return length(value) - 1
}

function trimmed(text,   copy) {
  copy = text
  sub(/^[ \t]+/, "", copy)
  return copy
}

function report(number, category, text) {
  if (!all_added && !(number in is_added)) return
  printf "%s:%d: [%s] %s\n", file, number, category, trimmed(text)
  found++
}

function opens_docstring(text) {
  return text ~ /^[ \t]*[rRuUbBfF]{0,2}("""|''')/
}

function docstring_length(start,   quote, index_, body) {
  quote = (line[start] ~ /"""/) ? "\"\"\"" : "'''"
  body = line[start]
  sub(/^[ \t]*[rRuUbBfF]{0,2}/, "", body)
  body = substr(body, 4)
  if (index(body, quote) > 0) return 1
  for (index_ = start + 1; index_ <= total; index_++)
    if (index(line[index_], quote) > 0) return index_ - start + 1
  return total - start + 1
}

function first_added(from, to,   index_) {
  if (all_added) return from
  for (index_ = from; index_ <= to; index_++)
    if (index_ in is_added) return index_
  return 0
}

function select_syntax(name) {
  BLOCK_MAX_LINES = 5
  DENSITY_MAX_LINES = 10
  if (name == "yaml") {
    assignment_pattern = "^[ \t]*-?[ \t]*[\"']?[A-Za-z_][A-Za-z0-9_.-]*[\"']?[ \t]*(:|=)"
    checks_volume = 1
    BLOCK_MAX_LINES = 3
    DENSITY_MAX_LINES = 5
  } else if (name == "just") {
    assignment_pattern = "^[ \t]*(export[ \t]+)?[A-Za-z_][A-Za-z0-9_-]*[ \t]*:="
    checks_volume = 1
    BLOCK_MAX_LINES = 2
    DENSITY_MAX_LINES = 3
  } else if (name == "terraform") {
    assignment_pattern = "^[ \t]*[A-Za-z_][A-Za-z0-9_-]*[ \t]*=[^=]"
    checks_volume = 1
    checks_descriptions = 1
    BLOCK_MAX_LINES = 3
    DENSITY_MAX_LINES = 5
  } else if (name == "shell") {
    assignment_pattern = "^[ \t]*(export[ \t]+|local[ \t]+|readonly[ \t]+)?[A-Za-z_][A-Za-z0-9_]*="
    checks_volume = 1
    allows_file_header = 1
  } else if (name == "javascript") {
    assignment_pattern = "^[ \t]*((const|let|var)[ \t]+)?[A-Za-z_$][A-Za-z0-9_$.\\[\\]']*[ \t]*=[^=]"
    comment_is_slash = 1
    checks_volume = 1
    allows_file_header = 1
  } else if (name == "rust") {
    assignment_pattern = "^[ \t]*(let|const|static)[ \t]+(mut[ \t]+)?[A-Za-z_][A-Za-z0-9_]*[^=]*=[^=>]"
    comment_is_slash = 1
    doc_comments_are_code = 1
    rust_inline = 1
    checks_volume = 1
    BLOCK_MAX_LINES = 3
    DENSITY_MAX_LINES = 5
  } else {
    assignment_pattern = "^[ \t]*[A-Za-z_][A-Za-z0-9_.\\[\\]'\"]*[ \t]*(:[^=]*)?[-+*/|&^%]?=[^=]"
    checks_header = 1
    checks_docstring = 1
    DENSITY_MAX_LINES = 5
  }
}

BEGIN {
  inline_pattern = "^[^\"'#]*[^ ]  +(#|\\/\\/)[ \t]*[A-Za-z]"
  MODULE_DOCSTRING_MAX_LINES = 3
  DESCRIPTION_MAX_CHARS = 120
  select_syntax(syntax)
  if (rust_inline) inline_pattern = "^[^\"]*[;,] +\\/\\/[ \t]*[A-Za-z]"
  if (added == "ALL") all_added = 1
  else {
    count = split(added, numbers, ",")
    for (index_ = 1; index_ <= count; index_++)
      if (numbers[index_] != "") is_added[numbers[index_] + 0] = 1
  }
}

{ line[NR] = $0 }

END {
  total = NR

  for (i = 1; i <= total; i++)
    if (!is_comment(line[i])) code_text = code_text "\n" line[i]

  for (i = 1; i <= total; i++) {
    text = line[i]
    if (is_blank(text) || is_exempt(text)) continue
    if (is_comment(text)) { header[++header_count] = i; continue }
    first_statement = i
    break
  }

  if (checks_header)
    for (i = 1; i <= header_count; i++)
      report(header[i], "HEADER", line[header[i]])

  if (checks_docstring && first_statement && opens_docstring(line[first_statement]) \
      && docstring_length(first_statement) >= MODULE_DOCSTRING_MAX_LINES)
    report(first_statement, "MODULE-DOCSTRING", line[first_statement])

  if (checks_volume)
    for (i = 1; i <= total; i++) {
      if (!is_comment(line[i]) || is_exempt(line[i])) continue
      for (run_end = i; run_end < total && is_comment(line[run_end + 1]) \
           && !is_exempt(line[run_end + 1]); run_end++) continue
      if (allows_file_header && i < first_statement) { i = run_end; continue }
      if (run_end - i + 1 >= BLOCK_MAX_LINES && (anchor = first_added(i, run_end))) {
        report(anchor, "BLOCK", line[anchor])
        for (j = i; j <= run_end; j++) in_reported_block[j] = 1
      }
      i = run_end
    }

  for (i = 1; i <= total; i++) {
    text = line[i]

    if (!is_comment(text)) {
      if (is_assignment(text) && text ~ inline_pattern)
        report(i, "INLINE", text)
      if (checks_descriptions && description_length(text) > DESCRIPTION_MAX_CHARS)
        report(i, "DESCRIPTION", text)
      continue
    }
    if (is_exempt(text) || ((checks_header || allows_file_header) && i < first_statement))
      continue

    if (all_added || i in is_added) added_comments++
    if (i in in_reported_block) continue
    if (!first_density_line && (all_added || i in is_added)) first_density_line = i

    if (text ~ /^[ \t]*(#|\/\/)[ \t]*[-=*_~#]{3,}/)
      report(i, "BANNER", text)
    else if (text ~ /^[ \t]*(#|\/\/)[ \t]*([Ss]tep|STEP|[Pp]hase|[Pp]art|[Ss]ection)[ \t]*[0-9:]/ || text ~ /^[ \t]*(#|\/\/)[ \t]*[0-9]+[.)][ \t]/)
      report(i, "STEP", text)
    else if (text ~ /^[ \t]*(#|\/\/)[ \t]*(Now|We|Here|This|These|First|Then|Next|Finally|Note|Notice|Create|Build|Get|Set|Loop|Check|Make|Ensure|Handle|Convert|Initialize|Extract|Return|Add|Update|Remove|Iterate|Parse|Store|Save|Load|Compute|Calculate|Validate|Fallback|Helper|Prepare|Apply|Start|Run|Use|Keep|Track|Find|Filter|Sort|Group|Merge|Wrap|Call|Send|Fetch|Read|Write|Open|Close|Skip|Default)([ \t]|'s)/)
      report(i, "NARRATIVE", text)
    else if (!is_comment(line[i - 1]) && !is_comment(line[i + 1])) {
      for (j = i + 1; j <= total && is_blank(line[j]); j++) continue
      if (j <= total && is_assignment(line[j]))
        report(i, "VARIABLE", text)
      else
        scan_remote(i, text)
    }
    else scan_remote(i, text)
  }

  if (checks_volume && added_comments >= DENSITY_MAX_LINES && first_density_line)
    report(first_density_line, "DENSITY", added_comments " comment lines in this change")
  else if (!checks_volume && added_comments >= DENSITY_MAX_LINES && (all_added || found))
    printf "%s: %d comment lines in this change — comments are the exception here, not the norm.\n", file, added_comments

  exit (found > 0) ? 1 : 0
}
