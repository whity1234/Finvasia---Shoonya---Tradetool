# Disclaimer 

I am not a very good coder. I have tried to build a tool, for my own trading purpose.
This tool needs extensive testing before using it and there is no gurantee, that it will work 100%
This code may not be the best code as I am a beginner. You would mostly need some python coding experience, to understand what is happening in the code.

# USE AT YOUR OWN RISK!!

# NOTE

This tool is mainly built for option selling.

This tool needs integration with Finvasia API, to function.

# Indices available to trade


![screenshot](https://github.com/whity1234/Finvasia-Tradetool/blob/main/Indices.png)

# Expiries parsed separately for each Index. Below example for BN
![screenshot](https://github.com/whity1234/Finvasia-Tradetool/blob/main/Expiries.PNG)




# KNOWN ISSUES
At depths of above 8, delays in websocket data were noticed. This is due to the code quality issue.

# SUPPORT
I dont commit to supporting any help requests for this code.

# Steps to run this tool:

1. You need to install pre-requsites from https://github.com/Shoonya-Dev/ShoonyaApi-py/blob/master/requirements.txt
2. Install other requirements using pip install commands.
3. Update the config.ini for user specific data
4. Use the login button to Login and 
5. Once the index is selected, it by default switches to the current weekly expiry automatically.
6. If required to switch to any other expiry, it needs to be selected from the expiries drop down menu, as given above.
7. Once all needed properties are selected, click on Update button.
8. Click on Refresh LTP and Qtys to refresh the prices and qty of hedges manually.(LTPs of other strikes are updated in real time automatically)

![screenshot](https://github.com/whity1234/Finvasia-Tradetool/blob/main/Screenshot.png)

https://t.me/Finvasia_Tool


# USE AT YOUR OWN RISK!!
