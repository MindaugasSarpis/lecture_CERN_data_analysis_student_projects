Wow! I actually made this, so let me tell you all about it.

> If you wish to run scripts yourself, start with `check_libraries.py`. After that feel free to run `get_one_year_data.py` to get data or `create_visuals.py` to make graphs. 

For this project I really wanted to use APIs. I've heard a lot about them, but didn't have a chance to try them myself; APIs were kinda intimidating for me. 

And since this subject comes from Physics faculty, I wanted to take on a physics topic, since I don't see such things very often. 

And then that NASA lecture gave me a final push towards NASA APIs.

Actually, at first I wanted to review weather on Mars: it seemed interesting and fairly simple to try and find patters in that data. However, that project was closed years ago, and the API was practically dead... So I chose NEO API, since it provided steady data even to this day.

> To get all needed data I made two scripts: `get_one_day_data.py` gets data for one day (I used it mostly for testing) and `get_one_year_data.py` gets data for a range of dates, though I used it only for yearly data.

NEO API keeps track of Near Earth Objects which come close to Earth each day. There are many different records, but I focused only on some of them. The number of objects, the difference of diameters, the velocity, the miss distance and the orbital period. The number is needed for a general idea; the diameter difference might show what causes the difference and last three entries allow to see different trends. 

> Use `create_visuals.py` to create graphs. It can take either Google Drive link (make sure link is accessible) or .csv file. It should be accissible too, duh. You'll have three different plot options; each option can be customised. For 'scatter' plot option I advise using "_sentry.csv" files or files with less data. 6000+ look really messy. 

Ah yes, sentry objects! Did you know that these sentry objects have non-zero chance of hitting Earth in the next 100 years? I decided to review them more closely to see if they show different trends than all NEOs. (They actually more dangerous then so called "potentially_hazardous" objects... Now you know.)

And to finish this project I used a script to make simple .pdf file with graphs with default options. 

> Use `make_pdf.py` to make your own file. Don't forget to specify data file you want to use; you can give it your own name if you wish.

And that's all. Thank you for seeing this!

Ah, and the biggest challenge was making all the graphs look good... Though I don't think it's really possible with 6k entries anyway.

Hmm, if I were to continue this project... I would make a function to extract only unique NEOs. 