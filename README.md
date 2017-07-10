# INGRESS_CAPTURE_LOG

## DESCRPTION
Fetch the comm log within a specific area, and logging the capture information.
Thanks for the ingrex_lib project(https://github.com/blackgear/ingrex_lib). It is implemented and enhanced a lot in my code.
Note: The scripts now are running in my server without any human interruption. So the scripts won't be changed very frequently.


## INTRODUCTION
1. refreshPortal.py

    Use Linux crontab to refresh portal's owner and team every 30 minutes. 

2. refreshCookies.py

    Specify your ingress account, and get the latest SACSID. You can use Linux crontab to refresh the cookies timely.

3. calculateTilekeys.py

    Calculate tilekeys for the newly added portals. And wait for being refreshed by field.py.

4. comm.py

    Fetch comm log within a specific area. Refresh the portal details if the player action is 'captured' or 'destroyed a Resonator on'.

5. field.py

    Fetch all the portals in one tilekey, and refresh the capture status.

## HOWTO
You can specify the max/min lat/lng (ex, your city), and then use linux crontab to run the scripts timely like this:

0 */3 * * * /usr/bin/python /root/refreshCookies.py >> /root/refreshCookies.log 2>&1

*/2 * * * * /usr/bin/python /root/comm.py >> /root/comm.log 2>&1

*/15 * * * * /usr/bin/python /root/calculateTilekeys.py >> /root/caltilekey.log 2>&1

*/30 * * * * /usr/bin/python /root/field.py >> /root/field.log 2>&1

*/30 * * * * /usr/bin/python /root/refreshPortals.py >> /root/refreshPortals.log 2>&1

As of now the scripts need database connection and don't have and UI. Maybe later I will try to do some coding for the UI part.
Hope you have a nice day with this script.


## LICENSE

The MIT License

Copyright (c) 2015 Daniel

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
