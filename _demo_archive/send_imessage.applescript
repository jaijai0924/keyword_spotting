on run {targetPhoneNumber, targetMessage}
    tell application "Messages"
        set targetService to 1st account whose service type = iMessage
        set targetBuddy to buddy targetPhoneNumber of targetService
        send targetMessage to targetBuddy
    end tell
end run