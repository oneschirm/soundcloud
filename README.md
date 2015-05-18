*cloud-cli*

cloud-cli is a simple utility to download your likes to your computer, appending relevant MP3 tags (ID3 tags) along the way. 

**Usage**

First, [register for API keys.](https://soundcloud.com/login?return_to=%2Fyou%2Fapps%2Fnew)

Define a URL to use for authentication, or use [mine](http://www.decaffeinated.io/projects/sc_code.html). If you use a different URL, you'll need to modify the code. 

Once you have your client key and your secret key, define them in your environment variables by susing `export SC_CLIENT="value"` and `export SC_SECRET="value."` If you're using a virtual environment, you may want to define them in your `/bin/activate` script then run it using `./bin/activate.`
 
Now you're set to run the script. Use `python3 (or bin/python3.4) cloud-cli.py` to start. You'll be given a link to use. Approve the app, then extract the value of the "code" URL parameter and paste it back into the script. 

The app will now attempt to download all of your likes in a `/soundcloud_downloads` directory and save your auth token in an `access.pkl` file for next time. 

**Limitations**

This script could obviously be repurposed to download a number of different things from Soundcloud -- playlists, other users' likes, your own posted songs. But right now it only handles likes. 

The soundcloud API (particularly the nexthref function) is [BROKEN](https://twitter.com/soundclouddev/status/564649386517737472) and only allows for fetching a total of 400 likes (maximum per call is 200 and only two calls work). So if you have more than that many songs, you may be out of luck. 

I'm only defining the artist (TPE1), title (TIT2) publisher (TPUB, but actually just the permalink) and comments (description plus tags) for the ID3 tagging. I hope this is sufficient for most -- other attributes didn't map over very easily. 
