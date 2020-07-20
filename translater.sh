#!/usr/bin/env bash
#/usr/bin/env sh
set -x

extract_words() {
    pybabel extract -F "$PWD"/babel.cfg -k lazy_gettext -o "$PWD"/messages.pot $1
}

produce_translations() {
   pybabel init -i "$PWD"/messages.pot -d "$PWD"/zopsedu/locale/ -l $1
}

compile_translations() {
  pybabel compile -d "$PWD"/zopsedu/locale/
}

update_translations() {
    pybabel update -i "$PWD"/messages.pot -d $1/locale
}

main() {
case "$1" in
    extract)
        shift
        extract_words $1
    ;;
    produce)
        shift
        produce_translations $1
    ;;
    compile)
        compile_translations
    ;;
    update)
        shift
        extract_words $1
        update_translations $1
    ;;
    --help)
        echo "usage:
                  extract [project_path]   Extracts words from jinja2(html) and python files.
                  produce [language_code]  Produces translations for given language_code.
                  compile                  Compiles translation files.
                  update  [project_path] [language_code]  Updates words and produces translation files.
             "
    ;;
esac
}

main "$@"

set +x
