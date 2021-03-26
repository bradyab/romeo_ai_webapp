# Running the App on Repl.it
- Hit run. A console and rendering of the site should pop up on the right. If you make code changes, you need to re-run (Cmd+Enter) then refresh the site preview panel
- Simply press "submit" on the webpage to use our demo facebook credentials, OR follow the instructions on the site if you want to integrate your own tinder account.

# Notes
- The prod site is hosted [here](https://romeoai.bradyab.repl.co)
- bradyab/romeo.ai is our "prod" server, to be used for demos with customers. Please fork this repl (need repl.it premium - ask Brady) and create a new branch to make changes and only merge them back to master once you verify they don't break anything
- The demo facebook credential string is set using the instructions given on the webpage, and is subsequently assigned to the variable form_text in `tinder_api.py` if no text box input is given. The facebook and tinder API tokens appear to be valid for a few days.
- the repl will crash with inline matplotlib plots. When this happens, use the shell cmd `pkill init` to forcefully restart the repl. Prevent this with `import matplotlib;
matplotlib.use('Agg')`
- make a tinder account with a fake facebook acct, add some photos and a bio, and start swiping/sending messages so you have some data to play with and you can get to know your user
- auth flow is hacky for now - We have to be careful to do any FB auth in browser to avoid people giving us their login info (security/trust hazard) and make sure we aren't incurring any facebook activity from replits servers (which, due to their obscure location, will trigger a suspicious activity FB security flag and force a password reset).
- for this reason, it also seems that you should only login to facebook from the same location that the account in question normally logs in from
- get_fb_id() calls some other FB API and is still called from main.py (i.e. replit's servers). Doesn't look like this one will force a password reset yet. Should be okay since this has been used since 3/23 with no issues
- The repl.it IDE is kinda wonky - if you get `TabError: inconsistent use of tabs and spaces in indentation` errors, open the code in VSCode, hit Ctrl-Shift-P and select `convert indentation to spaces` to fix, then commit and push
