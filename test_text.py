import subprocess

def send_imessage(email, message):
    script = """
    on run {targetEmail, targetMessage}
        tell application "Messages"
            set targetService to 1st account whose service type = iMessage
            set targetBuddy to buddy targetEmail of targetService
            send targetMessage to targetBuddy
        end tell
    end run
    """

    apple_script = f"""
    osascript -e '{script}' '{email}' '{message}'
    """

    process = subprocess.Popen(apple_script, shell=True, stdout=subprocess.PIPE)
    process.wait()
    result = process.stdout.read()
    return result

# Example usage
email = "jaijaimacabangon@gmail.com"
message = "Hello from Python!"
send_imessage(email, message)