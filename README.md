Random album cover generator
============================

Just a fun little project I hacked together in 2015 to generate a random band name, album title and a cover for it.

Runs on <https://rotzooi.bad-bit.net/randomcover> if you want to try it.

It picks:
- A random Wikipedia page title to generate a band name
- A random quote from Wikiquote to generate an album title
- A random photo from the 'most interesting in the past 7 days' page on Flickr

I'm not sure where these instructions originated from, I think I came across it on Reddit or some such. Tweaked it a bit to generate better results.

Please keep in mind that this was just a quick and dirty fun hacking project and this is by no means production-quality code :-)

Installing
----------
Needs at least Python 3.6 with pip.

```
pip3 install -r requirements.txt
```

Or, if you want to run within a virtual environment (I'd always recommend this, although it is not so useful for this almost-no-dependencies pet project):

```
virtualenv -p python3 venv
venv/bin/pip install -r requirements.txt
```

Installing as a service
-----------------------
Not sure why you would want this, but here goes. We assume you've cloned this repo to `/var/www/randomcover`, and that you're running Ubuntu/Debian with systemd.

First, create a virtual environment and install the requirements into it:
```
cd /var/www/randomcover
virtualenv -p python3 venv
venv/bin/pip install -r requirements.txt
```

Next, copy the systemd unit file (included in this repo) and enable it:
```
sudo cp randomcover.service /etc/systemd/system/
sudo vim /etc/systemd/system/randomcover.service  # If you need to edit paths / commandline parameters
sudo systemctl daemon-reload
sudo systemctl enable randomcover
sudo service randomcover start
```


Running
-------
On your main python install:
```
python3 serve.py
```

Or in a virtual environment (see 'Installation' above):
```
venv/bin/python serve.py
```

For command-line options, see
```
venv/bin/python serve.py --help
```
