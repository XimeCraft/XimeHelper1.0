on run argv
    set targetFile to item 1 of argv
    set targetName to item 2 of argv
    set appName to item 3 of argv
    
    tell application "System Events"
        tell application appName
            set windowList to every window
            repeat with theWindow in windowList
                if name of theWindow contains targetName then
                    -- Try to save
                    try
                        keystroke "s" using command down
                        delay 0.5
                    end try
                    -- Close window
                    close theWindow
                    exit repeat
                end if
            end repeat
        end tell
    end tell
end run 