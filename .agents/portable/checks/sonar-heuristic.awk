# Flag, on selected lines of a JavaScript file, the patterns SonarQube reports
# most often on this kind of code and that no linter rule covers.
#
# -v file=<path>    name to print in the report
# -v added=<list>   comma-separated line numbers to report on, or ALL

function is_added(number) { return added == "ALL" || (number in added_line) }

function report(rule, message) {
  printf "%s:%d: %s %s\n", file, FNR, rule, message
}

BEGIN {
  count = split(added, numbers, ",")
  for (index_ = 1; index_ <= count; index_++)
    if (numbers[index_] != "") added_line[numbers[index_] + 0] = 1
}

!is_added(FNR) { next }

/(^|[^.[:alnum:]_])window\./ { report("S7764", "use globalThis instead of window") }
/\.replace\(\/.*\/[a-z]*g[a-z]*[ \t]*,/ { report("S7781", "use replaceAll() instead of replace() with a global regex") }
/(get|set|has|remove)Attribute\([ \t]*["']data-/ { report("S7761", "use .dataset instead of a data-* attribute call") }
/\.(last)?[iI]ndexOf\([^)]*\)[ \t]*(!==|===|!=|==|>=|<|>)[ \t]*-?[01]/ { report("S7765", "use .includes() instead of an indexOf() comparison") }
/\.removeChild\(/ { report("S7762", "use node.remove() instead of removeChild()") }
/Object\.assign\([ \t]*\{/ { report("S6661", "use object spread instead of Object.assign({}, ...)") }
