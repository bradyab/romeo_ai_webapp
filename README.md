# Running the App
- Open main.py 
- Hit run. A stdout and rendering of the site should pop up on the right. 
- Simply press "submit" on the webpage to use the default facebook credentials. Follow the instructions on the site if you want to integrate your own tinder account.
- The default facebook credentials are set using the instructions on the webpage, then setting that string as the placeholder for the textbox in `templates/form.html` so you don't have to ctrl-v it in every time. The facebook credentials appear to be valid for more than 24 hours.

# Notes
- the repl will crash with inline matplotlib plots. When this happens, use the shell cmd `pkill init` to forcefully restart the repl. Prevent this with `import matplotlib;
matplotlib.use('Agg')`
- make a tinder account with a fake facebook acct, add some photos and a bio, and start swiping/sending messages so you have some data to play with and you can get to know your user
- auth flow is hacky for now - We have to be careful to do any FB auth in browser to avoid people giving us their login info (security/trust hazard) and make sure we aren't incurring any facebook activity from replits servers (which, due to their obscure location, will trigger a suspicious activity FB security flag and force a password reset).
- for this reason, it also seems that you should only login to facebook from the same location that the account in question normally logs in from
- get_fb_id() calls some other FB API and is still called from main.py (i.e. replit's servers). Doesn't look like this one will force a password reset yet. Should be okay since this has been used since 3/23 with no issues 