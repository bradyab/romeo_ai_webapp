# Overview

[This webapp](https://romeoai.bradyab.repl.co/) integrates with your Tinder account to give you profile tips, constructive feedback, and strategies to have more meaningful conversations in dating apps. To date, it: 
- provides a breakdown of the swipe-right-rates of all your profile pictures
- performs sentiment analysis on messages when you were ghosted
- identifies frequent coversation topics 1) when you had extended conversation with matches, and 2) when you were ghosted by matches
- calculates opening line response rates for specific opening lines and categories of opening lines like "references match's bio/job/school" 


# Running the App on Repl.it
- Hit run. A console and rendering of the site should pop up on the right. If you make code changes, you need to re-run (Cmd+Enter) then refresh the site preview panel
- Simply press "submit" on the webpage to use our demo facebook credentials, OR follow the instructions on the site if you want to integrate your own tinder account.

# Development
- Please fork this repl (you'll need repl.it premium - ask Brady) and create a new branch to make changes. Only merge them back to master once you verify they don't break anything
- bradyab/romeo.ai, hosted [here](https://romeoai.bradyab.repl.co), is our "prod" server. It should be set to "always on" and is to be used for demos with customers. Whenever changes to master are merged, we need to deploy them by pulling the changes to that repl and rerunning 
- The demo facebook credential string is set using the instructions given on the webpage, and is subsequently assigned to the variable form_text in `tinder_api.py` if no text box input is given. The facebook and tinder API tokens appear to be valid for a few days.
- make a tinder account with a fake facebook acct, add some photos and a bio, and start swiping/sending messages so you have some data to play with and you can get to know your user
- auth flow is hacky for now - We have to be careful to do any FB auth in browser to avoid people giving us their login info (security/trust hazard) and make sure we aren't incurring any facebook activity from replits servers (which, due to their obscure location, will trigger a suspicious activity FB security flag and force a password reset).
- for this reason, it also seems that you should only login to facebook from the same location that the account in question normally logs in from
- get_fb_id() calls some other FB API and is still called from main.py (i.e. replit's servers). Doesn't look like this one will force a password reset yet. Should be okay since this has been used since 3/23 with no issues. Brady got email from FB about iOS login 3/25

# Troubleshooting
- The repl.it IDE is kinda wonky - if you get `TabError: inconsistent use of tabs and spaces in indentation` errors, try hitting the white square in the top right of the IDE to auto-format your code. If that doesn't work, try the advice [here](https://replit.com/talk/ask/TabError-inconsistent-use-of-tabs-and-spaces-in-indentation/53231) or erase and re-add the tabs in the previous and next lines (you may have to do this recursively). If that doesn't work, open the code in VSCode, hit Ctrl-Shift-P and select `convert indentation to spaces` to fix, then commit and push
- If you're seeing an `Unable to connect to this GitHub repository` error in repl.it, make sure your changes are properly committed and pushed to a git branch. Don't throw away any code until you're sure that's been fixed
- the repl will crash with inline matplotlib plots. When this happens, use the shell cmd `pkill init` to forcefully restart the repl. Prevent this with `import matplotlib; matplotlib.use('Agg')`
