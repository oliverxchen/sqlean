#! /bin/bash

# Open iTerm and get window id for screencapture
open -a iTerm .
WINDOW_ID=`osascript -e 'tell app "iTerm" to id of window 1'`

function cmd_up() {
    osascript -e 'tell app "System Events" to key code 126 using command down'
}

function cmd_k() {
    osascript -e 'tell app "System Events" to key code 40 using command down'
}

function write_to_iterm() {
    COMMAND="tell app \"iTerm\"
    tell current session of window 1
        write text \"${1}\"
    end tell
end tell"
    osascript -e "$COMMAND"
}

function resize_iterm() {
    COMMAND="tell app \"iTerm\"
    set bounds of window 1 to {0, 0, 640, ${1}}
end tell"
    osascript -e "$COMMAND"
}

function screencap_window() {
    screencapture -o -l $WINDOW_ID -T 2 $1
}

function wrapper() {
    resize_iterm $1
    cmd_k
    write_to_iterm "$2"
    sleep 1
    cmd_up
    cmd_up
    screencap_window "$3"
}

write_to_iterm "make venv"
sleep 2

wrapper 280 "sqlean tests/fixtures/pass" "docs/img/pass_summary.png"
wrapper 490 "sqlean -d docs/examples/diff.sql" "docs/img/diff.png"
wrapper 490 "sqlean -v docs/examples/typo.sql" "docs/img/verbose.png"

# Cleanup -> exit from iTerm
osascript -e 'tell app "iTerm" to quit'
