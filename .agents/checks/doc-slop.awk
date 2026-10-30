# Reports a one-line Rust doc comment that only repeats the name of the
# item below it ("/// The points." above `fn points`) or is too short to
# add anything ("/// How many." above `count`). A doc quoting code or
# giving a unit is spared: that is what a doc is for. Run by doc-slop.sh.

function words(text, list,   count_, index_, word, kept) {
  gsub(/`[^`]*`/, " ", text)
  count_ = split(tolower(text), raw, /[^a-z]+/)
  kept = 0
  for (index_ = 1; index_ <= count_; index_++) {
    word = raw[index_]
    if (word == "" || word in STOP) continue
    sub(/s$/, "", word)
    list[++kept] = word
  }
  return kept
}

function name_tokens(declaration, tokens,   name, spaced, count_, index_) {
  name = declaration
  sub(/^[ \t]*(pub(\([a-z]+\))?[ \t]+)?((const|async|unsafe)[ \t]+)*(fn|struct|enum|trait|type|mod|const|static)?[ \t]*/, "", name)
  match(name, /^[A-Za-z_][A-Za-z0-9_]*/)
  if (RLENGTH <= 0) return 0
  name = substr(name, 1, RLENGTH)
  spaced = name
  gsub(/_/, " ", spaced)
  spaced = gensub(/([a-z0-9])([A-Z])/, "\\1 \\2", "g", spaced)
  count_ = split(tolower(spaced), tokens, / +/)
  for (index_ = 1; index_ <= count_; index_++) sub(/s$/, "", tokens[index_])
  return count_
}

function judge(   doc_count, name_count, index_, inner, known, said) {
  if (block_text ~ /`/ || tolower(block_text) ~ UNITS) return
  doc_count = words(block_text, said)
  if (doc_count <= 2) {
    printf "%s:%d: ECHO: two words or fewer cannot say what the name does not; delete it\n", FILENAME, block_line
    found = 1
    return
  }
  name_count = name_tokens($0, known)
  if (name_count == 0) return
  for (index_ = 1; index_ <= doc_count; index_++) {
    for (inner = 1; inner <= name_count; inner++) if (said[index_] == known[inner]) break
    if (inner > name_count) return
  }
  printf "%s:%d: ECHO: the doc only repeats the name; delete it or say what the name cannot\n", FILENAME, block_line
  found = 1
}

BEGIN {
  UNITS = "pixel|metre|meter|millimetre|radian|degree|second|hertz|percent"
  split("the a an of to in on for is its it and or this that with by as be one each every all", stop_list, " ")
  for (index_ in stop_list) STOP[stop_list[index_]] = 1
}

/^[ \t]*\/\/\/ ?/ {
  line_text = $0
  sub(/^[ \t]*\/\/\/ ?/, "", line_text)
  if (block_size == 0) block_line = FNR
  block_size++
  block_text = line_text
  next
}

/^[ \t]*#\[/ { next }

{
  if (block_size == 1 && block_text !~ /^#/) judge()
  block_size = 0
  block_text = ""
}

END { exit found }
