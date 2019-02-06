# gmail-trip-tracker


Will read your gmail for the location tracker emails, specifically.
It will crudely try to pull the month from the subject and the "cities visited" count from the body.
It will take that data and plot a line graph at http://127.0.0.1:5004

<h1>auth</h1>
Upon first run, the script will try to authenticate you using locally stored credentials. If they're not present, Google will launch a web browser to confirm you want THIS application to access your gMail. Once you grant permissions, the credentials will be stored locally and you will not have to launch the browser anymore. You can then copy your creds file across platforms to run as needed.

<h1>usage</h1>
```python gmail-trip-tracker.py```

Open web browser to: http://127.0.0.1:5004
