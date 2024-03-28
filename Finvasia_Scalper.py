from time import sleep
from tkinter import *
import tkinter as tk
from tkinter import ttk
import threading, json, math, sqlite3, logging, os, csv, time
from datetime import datetime, timedelta
from datetime import datetime as dt
from datetime import timedelta as td
from time import strftime
from api_helper import ShoonyaApiPy
import pandas as pd
from tkinter import simpledialog, filedialog, messagebox
import pyotp
import configparser
from pathlib import Path
import math
import json
from concurrent.futures import ThreadPoolExecutor
import requests
import zipfile
import os
import pandas as pd
import random
import threading as th
from random import randint

import warnings
import logging
import base64

import locale

locale.setlocale(locale.LC_MONETARY,'en_IN')



warnings.simplefilter(action='ignore', category=UserWarning)

pd.options.mode.chained_assignment = None


#logging.basicConfig(level=logging.DEBUG)


config = configparser.ConfigParser()
config.read("config.ini")

authotp = pyotp.TOTP(
    config.get("CRED", "authenticator")
).now()  # copy the authenticator code here in quote.

start = datetime.now()

api = ShoonyaApiPy()

call_strike_ltp = 0.0
put_strike_ltp = 0.0
token_ce = 0
token_pe = 0
bn_nifty_lp = 0.0
nifty_lp = 0.0
token = ""

Spot_LTP = 0.0
margin_available = 0.0
margin_used  = 0.0

ATM_strike = 0.0
comp_qty = 0

global First_strike,row,row_PE,weekly_expiry,index_symbol,exp,exch,masters,expiry_date
global s,away,xmm

s=0
q=0

away = 0

exp = 0

p = 1380



##Style

lbl_fonts = ("Helvetica 18 bold", 10)
btn_fonts = ("Helvatical bold", 10)
btn_fg = "White"
btn_bg = "Black"
lbl_fg = "white"
lbl_bg = "#ffffe6"
m2m_fonts = ("Helvatical bold", 10)
time_font = ("Helvatical bold", 10, "bold")
time_bg = "Green"
time_fg = "White"
top_lbl_fg = "Black"
top_lbl_bg = "Grey"
top_lbl_font = ("Helvatical bold", 10)
welcome_font = ("Helvatical bold", 10)
welcome_bg = "White"
welcome_fg = "Green"
refresh_font = ("Helvatical bold", 10)
refresh_bg = "White"
refresh_fg = "Green"



def fetch_api_keys(user_id, prism_password):
    try:
        # Create a session object
        session = requests.Session()

        # Make a POST request to the Prism login endpoint
        url_login = "https://prism.finvasia.com:9000/api/login"
        headers = {'Content-Type': 'application/json'}
        data = {'email': user_id, 'password': prism_password}
        response = session.post(url_login, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        response_json = response.json()
        #print(response_json)

        # Extract the user token from the response
        token = response_json['data']['user']['token']
        #print(token)

        # Make a POST request to the Prism refresh API key endpoint
        url_refresh = "https://prism.finvasia.com:9000/create_update/api/keys"
        headers = {'Authorization': 'Bearer ' + token}
        response = session.post(url_refresh, headers=headers)
        response.raise_for_status()
        #print(response.raise_for_status())

        # Make a POST request to the Prism fetch API key endpoint
        url_fetch = "https://prism.finvasia.com:9000/get/api/keys/detail"
        headers = {'Authorization': 'Bearer ' + token}
        response = session.post(url_fetch, headers=headers)
        response.raise_for_status()
        response_json = response.json()
        #print(response_json)

        # Extract the API key from the response
        api_key = response_json['data'][0]['ApiKey']
        #print(api_key)

        return api_key

    except requests.exceptions.RequestException as ex:
        # Handle exceptions
        print(ex)
        print("Generating API failed")
        return ''



def Login():  # Login function get the api login + username and cash margin
    print("In login")
    #time.sleep(2)
    global ret,token
    global get_username, get_pwd, get_Auth, get_vc, get_apikey,index_symbol,max_size,round_num,exch,masters
    global top
    #global depth,multiplier
    # depth = 10
    # multiplier = 1

    if index_symbol=="BANKNIFTY":
        token = 26009
        print("BANK")
        max_size = 450
        round_num = 15
        exch= "NFO"
        masters = 'NFO_symbols.txt'

    elif index_symbol=="FINNIFTY":
        token = 26037
        print("FINN")
        max_size = 1000
        round_num = 40
        exch= "NFO"
        masters = 'NFO_symbols.txt'

    elif index_symbol=="NIFTY":
        token = 26000
        print("NIFTY")
        max_size = 900
        round_num = 50
        exch= "NFO"
        masters = 'NFO_symbols.txt'

    elif index_symbol=="MIDCPNIFTY":
        token = 26074
        print("MIDCAP")
        max_size = 1500
        round_num = 75
        exch= "NFO"
        masters = 'NFO_symbols.txt'

    elif index_symbol=="BSXOPT":
        token = 1
        print("SENSEX")
        max_size = 1000
        round_num = 10
        exch= "BFO"
        masters = 'BFO_symbols.txt'

    elif index_symbol=="BKXOPT":
        token = 12
        print("BANKEX")
        max_size = 450
        round_num = 15
        exch= "BFO"
        masters = 'BFO_symbols.txt'


    try:
        try:

            ret = api.login(
            userid=config.get("CRED", "user"),
            password=config.get("CRED", "pwd"),
            twoFA=authotp,
            vendor_code=config.get("CRED", "vc"),
            api_secret=key,
            imei=config.get("CRED", "imei"),
            )
            #print(ret)


        except Exception as e:
            ret = api.login(
                userid=config.get("CRED", "user"),
                password=config.get("CRED", "pwd"),
                twoFA=authotp,
                vendor_code=config.get("CRED", "vc"),
                api_secret=config.get("CRED", "api_key"),
                imei=config.get("CRED", "imei"),
            )

        usersession = ret["susertoken"]

        #print(usersession)

        file = open("user_session.txt", "w")
        file.write(usersession)
        file.close()
        username = ret["uname"]
        #log(f"Sucessfully Login to the account {username}")

        print("Welcome!")
        username = ("Welcome")  # Just for hiding full name
        welcome_lbl["text"] = username

        setupwebsocket()
        sleep(0.5)

        #fetch_ATM(index_symbol)




    except Exception as e:
        #errorlog(f"an exception occurred :: {e} API ERROR")
        print(e)
        #if API_key is not working, gemerate new API_key from Prism and fetch here.
        print("Generating API Keys")
        api_key = fetch_api_keys(config.get("CRED", "user"),config.get("CRED", "prism_pass"))
        print(api_key)
        write_to_github_file(owner, repo, path, token, api_key)
        param = config["CRED"]
        param["api_key"] = api_key
        config.set("CRED", "api_key",api_key)
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
        print("Generated API Key, please login again")



def Logout():
    global ret, api, display_call_ltp, display_put_ltp

    try:
        destroy()
        api.unsubscribe(["NSE|26009", "NSE|26000"])
        #api.unsubscribe([f"NFO|{token_ce}", f"NFO|{token_pe}"])
        print("closing websocket")
        api.close_websocket()
        print("Logging out from API")
        api.logout()
        username = ret["uname"]
        username = "Bye Bye" + " " + str(username[:-10]) + "!"
        welcome_lbl["text"] = username

        display_call_ltp["text"] = 0.0
        display_put_ltp["text"] = 0.0
        Expiry_day_combo_box1.current(0)
        index_combo1box.current(0)
        Strike_combo_box1.current(0)
        qty_combo_box1.current(0)
        nifty_price_lbl["text"] = 0.0
        bnf_price_lbl["text"] = 0.0

        #log(f"Sucessfully Logged out from the account {username}")

    except Exception as e:
        print(e)
        #errorlog(f"an exception occurred :: {e} API ERROR")


root = Tk()
root.geometry("1500x600")
# Set the resizable property False
root.resizable(False, True)
#root.config(background="#ffffe6")
root.config(background="#808080")
root.title("FV Scalper App")
# root.wait_visibility(root)
# root.wm_attributes("-alpha", 0.5)
style = ttk.Style()
style.theme_use("alt")
#style.theme_use("winnative")  ## enable this for windows
style.configure('TButton', background = '#808080', foreground = 'black', width = 8)
style.map('TButton', background=[('active','red')])
#root.tk.call("wm", "iconphoto", root._w, tk.PhotoImage(file="richdotin.png"))
# root.iconbitmap(r'c:\Users\SN\exe\ShoonyaApi-py\richdotcom.ico')



Margin = Button(
    root,
    text="Margins",
    font=btn_fonts,
    fg=btn_fg,
    bg=btn_bg,
    bd=0,
    activeforeground="Red",
    command=lambda: margin_used(),
)
Margin.place(x=p, y=5)

Margin_lbl = Label(root, text=margin_available, bg="Orange", font=lbl_fonts)
Margin_lbl.place(x=p, y=25, width=100)

brokerage_lbl = Label(root, text="", fg="Black", font=lbl_fonts, bg="White")
brokerage_lbl.place(x=p, y=45,width=100)


Refresh_ltps_btn = Button(
    root,
    text="Refresh LTPs",
    font=btn_fonts,
    fg=btn_fg,
    bg=btn_bg,
    bd=1,
    activeforeground="Green",
    command=lambda: Refresh_LTPs(),
)
Refresh_ltps_btn.place(x=p, y=75)


Refresh_qtys_btn = Button(
    root,
    text="Refresh QTYs",
    font=btn_fonts,
    fg=btn_fg,
    bg=btn_bg,
    bd=1,
    activeforeground="Green",
    command=lambda: Refresh_qtys(),
)
Refresh_qtys_btn.place(x=p, y=95)



expiry_date_lbl = Label(root, text="", bg="Yellow", font=lbl_fonts)
expiry_date_lbl.place(x=p, y=120, width=80)

ATM_strike_label = Label(root, text="", fg="Black", font=lbl_fonts, bg="White")
ATM_strike_label.place(x=p, y=145)







# Login button
Login_btn = Button(
    root,
    text="Login",
    font=btn_fonts,
    fg=btn_fg,
    bg=btn_bg,
    bd=0,
    activeforeground="Green",
    command=lambda: Login(),
)
Login_btn.place(x=p, y=200)

# Logout button
Logout_btn = Button(
    root,
    text="Logout",
    font=btn_fonts,
    fg=btn_fg,
    bg=btn_bg,
    bd=0,
    activeforeground="Green",
    command=lambda: startThread(1),
)
Logout_btn.place(x=p, y=235)




def my_depth(*args):
    global depth
    y = (depth+1) * 2
    #global qty
    #try:
    depth = int(Depth_Values_combo_box1.get())



# Combobox 2
Depth_Values = ["Select Depth","0","5","8","12","14"]

Depth_Values_combo = tk.StringVar()
Depth_Values_combo_box1 = ttk.Combobox(
    root, values=Depth_Values, width=11, textvariable=Depth_Values_combo
)
Depth_Values_combo_box1 .place(x=p, y=330)
Depth_Values_combo_box1 .current(3)
Depth_Values_combo.trace("w", my_depth)
depth = int(Depth_Values_combo_box1.get())


def my_multiplier(*args):
    global multiplier
    #global qty
    #try:
    multiplier = int(qty_combo_box1.get())
    #print(multiplier)
    #     log(f"index selected is: {index_symbol}")
    # except Exception as e:
    #     errorlog(f"an exception occurred :: {e}")


# Combobox 3
qty_combo_value = ["Select Multiples", "1", "2", "3", "4", "5"]
qty_combo = tk.StringVar()
qty_combo_box1 = ttk.Combobox(
    root, values=qty_combo_value, width=10, textvariable=qty_combo
)
qty_combo_box1.place(x=p, y=360)
dt = datetime.now()
if dt.weekday() == 3 or dt.weekday() == 4 or dt.weekday() == 5:
    qty_combo_box1.current(1)
else:
    qty_combo_box1.current(1)

qty_combo.trace("w", my_multiplier)
multiplier = int(qty_combo_box1.get())



def my_away(*args):
    global away
    #global qty
    #try:
    away = int(away_combo_box1.get())
    print("AWAY",away)

#Combo Away

# Combobox 3
away_combo_value = ["Away", "0","4", "6", "8", "10", "12", "14"]
away_combo = tk.StringVar()
away_combo_box1 = ttk.Combobox(
    root, values=away_combo_value, width=10, textvariable=away_combo
)
away_combo_box1.place(x=p, y=390)
dt = datetime.now()
if dt.weekday() == 3 or dt.weekday() == 4 or dt.weekday() == 5:
    away_combo_box1.current(1)
else:
    away_combo_box1.current(1)

away_combo.trace("w", my_away)
#away = int(away_combo_box1.get())
#print("AWAY",away)


def margin_used():
    #print(api.get_limits())
    limit = api.get_limits()
    #print("Limits",limit)
    # key = "marginused"
    # if key in limit.values():
    
    margin_used2 = (float((limit['marginused'])))
    #margin_used2 = 0
    #print(margin_used)

    Cash = float((limit['cash']))
    payin = float((limit['payin']))
    brokerage = float((limit['brokerage']))
    #cash_coll = (float((limit['collateral'])))
    cash_coll = 0
    margin_available =(cash_coll+payin+Cash)-margin_used2
    margin_available = round(margin_available,2)
    #print (margin_available)
    Margin_lbl["text"] = locale.currency(margin_available,grouping=True)
    brokerage_lbl["text"] = locale.currency(brokerage,grouping=True)

def my_distance(*args):
    global distance,exp
    exp = 1

    distance = int(BN_dist_combo_box1.get())
    #print("Selection",distance)


# Combobox 2
BN_dist = ["BN Distance","100","500"]

BN_dist_combo = tk.StringVar()
BN_dist_combo_box1 = ttk.Combobox(
    root, values=BN_dist, width=11, textvariable=BN_dist_combo
)
BN_dist_combo_box1 .place(x=p, y=415)
BN_dist_combo_box1 .current(1)
BN_dist_combo.trace("w", my_distance)
distance = int(BN_dist_combo_box1.get())



Update_btn = Button(
    root,
    text="Update",
    font=btn_fonts,
    fg=btn_fg,
    bg=btn_bg,
    bd=0,
    activeforeground="Green",
    command=lambda: startThread(2),
)
Update_btn.place(x=p, y=445)

destroy = Button(
    root,
    text="Destroy",
    font=btn_fonts,
    fg=btn_fg,
    bg=btn_bg,
    bd=0,
    activeforeground="Green",
    command=lambda: startThread(4),
)
destroy.place(x=p, y=465)


Orderbook = Button(
    root,
    text="Fetch OB",
    font=btn_fonts,
    fg=btn_fg,
    bg=btn_bg,
    bd=0,
    activeforeground="Green",
    command=lambda: cancel_order(),
)
Orderbook.place(x=p, y=515)



welcome_lbl = Label(root, text="", fg="Green", font=lbl_fonts, bg="White")
welcome_lbl.place(x=p, y=490)


Sq_btn = Button(
    root,
    text="Square off Shorts",
    font=btn_fonts,
    fg=btn_fg,
    bg=btn_bg,
    bd=0,
    activeforeground="Red",
    command=lambda: Squareoff_all(-1),
)
Sq_btn.place(x=p, y=560)

Sq_all_btn = Button(
    root,
    text="Square off All",
    font=btn_fonts,
    fg=btn_fg,
    bg=btn_bg,
    bd=0,
    activeforeground="Red",
    command=lambda: Squareoff_all(1),
)
Sq_all_btn.place(x=20, y=570)
            

# masters =""

# if index_symbol == "BANKNIFTY" or "NIFTY" or "FINNIFTY":
#     masters == "NFO_symbols.txt"
# else:
#     masters == "BFO_symbols.txt"


def my_index(*args):
    print("in My index")
    global index_symbol,max_size,round_num,exch,masters


    #global qty
    try:
        index_symbol = index_combo1box.get()
        download_instruments_csv()
        print(index_symbol)

        if index_symbol=="BANKNIFTY":
            token = 26009
            print("BANK")
            max_size = 450
            round_num = 15
            exch= "NFO"
            masters = 'NFO_symbols.txt'

        elif index_symbol=="FINNIFTY":
            token = 26037
            print("FINN")
            max_size = 1000
            round_num = 40
            exch= "NFO"
            masters = 'NFO_symbols.txt'

        elif index_symbol=="NIFTY":
            token = 26000
            print("NIFTY")
            max_size = 900
            round_num = 50
            exch= "NFO"
            masters = 'NFO_symbols.txt'

        elif index_symbol=="MIDCPNIFTY":
            token = 26074
            print("MIDCAP")
            max_size = 750
            round_num = 75
            exch= "NFO"
            masters = 'NFO_symbols.txt'

        elif index_symbol=="BSXOPT":
            token = 1
            print("SENSEX")
            max_size = 500
            round_num = 10
            exch= "BFO"
            masters = 'BFO_symbols.txt'

        elif index_symbol=="BKXOPT":
            token = 12
            print("BANKEX")
            max_size = 450
            round_num = 15
            exch= "BFO"
            masters = 'BFO_symbols.txt'
            print(masters)


        get_weekly_expiry_date(index_symbol)
        expiry_combo1box['values'] = weekly_expiry


        #log(f"index selected is: {index_symbol}")
    except Exception as e:
        print(e)
        #errorlog(f"an exception occurred :: {e}")

### Combobox
# Combobox 0
index_values1 = ["Select Index","NIFTY", "BANKNIFTY","FINNIFTY","MIDCPNIFTY", "BSXOPT","BKXOPT"]
index_combo1 = tk.StringVar()
index_combo1box = ttk.Combobox(
    root, values=index_values1, width=11, textvariable=index_combo1
)
index_combo1box.place(x=p, y=265)



# 0 Monday,# 1 Tuesday,# 2 Wednesday,# 3 Thursday,# 4 Friday

dt = datetime.now()
#print(dt.weekday())

if dt.weekday() == 4 or dt.weekday() == 0 or dt.weekday() ==1 or dt.weekday() ==5 or dt.weekday() ==6 :
    index_combo1box.current(6)
elif dt.weekday() ==2:
    index_combo1box.current(2)
elif dt.weekday() ==3:
    index_combo1box.current(1)

index_combo1box.current(2)
    

index_combo1.trace("w", my_index)
index_symbol = index_combo1box.get()
print(index_symbol)
#my_index()



def get_weekly_expiry_date(index_symbol):
    global expiry_date,weekly_expiry,exch,masters

    print("inside get_weekly_expiry_date")

    print(index_symbol)

    if index_symbol =="BANKNIFTY" or index_symbol =="FINNIFTY" or index_symbol =="NIFTY":
        masters ='NFO_symbols.txt'
        exch = "NFO"

    else:
        masters ='BFO_symbols.txt'
        exch = "BFO"


    symboldf = pd.read_csv(masters)
    #print(symboldf)
    df = symboldf[(symboldf.Exchange == exch) & (symboldf.Symbol == index_symbol)]
    df['Expiry'] = pd.to_datetime(df['Expiry']).apply(lambda x: x.date())
    #df.drop(df[df.Expiry <datetime.datetime.now().date()].index, inplace=True)
    weekly_expiry = df[df.Exchange == exch]['Expiry'].unique().tolist()
    weekly_expiry.sort()

    weekly_expiry = [str(d.strftime('%d-%b-%Y').upper()) for d in weekly_expiry]
    #print(weekly_expiry)

    #thu = [str(x) for x in thu]

    thu = weekly_expiry[0]

    #print(thu)

    #print("inside get_weekly_expiry_date",thu)

    #thu = "28-SEP-2023"

    expiry_date_lbl["text"] = thu
    expiry_date = thu

    return thu



def download_instruments_csv():

    

    #expiry_date = get_weekly_expiry_date(index_symbol)
    if index_symbol == "BSXOPT" or index_symbol == "BKXOPT":
        print("Downloading BFO MAster file")
        url = 'https://api.shoonya.com/BFO_symbols.txt.zip'
        modTimesinceEpoc = os.path.getmtime('./BFO_symbols.txt')
        zip_file = 'BFO_symbols.txt.zip'
    else:
        print("Downloading NFO Master file")
        url = 'https://api.shoonya.com/NFO_symbols.txt.zip'
        modTimesinceEpoc = os.path.getmtime('./NFO_symbols.txt')
        zip_file = 'NFO_symbols.txt.zip'

    #print(url)

    today = float(time.time())
    #print(today)

    today2 = datetime.today()

    date_string = today2.strftime('%d-%B-%Y')
    date_string = date_string.upper()

    p = (today - modTimesinceEpoc)/86400
    #print("Instruments.csv:",p)

    #if p > 0 or expiry_date < date_string:
    if p > 0:
        #print("Downloading Masters file") 
        r = requests.get(url, allow_redirects=True)
        #print(r)
        open(zip_file, 'wb').write(r.content)
        file_to_extract = zip_file.split()
     
        try:
            with zipfile.ZipFile(zip_file) as z:
                z.extractall()
                print("Extracted: ", zip_file)
        except:
            print("Invalid file")

        os.remove(zip_file)
        #print(f'remove: {zip_file}')
        # read_file = pd.read_csv (r'NFO_symbols.txt')
        # read_file.to_excel (r'NFO_Masters.xlsx', index = None, header=True)

    else:
        print("Skipping Instruments.csv download")
        #Mon0,Tue1,Wed2,Thu3,Fri4,Sat5,Sun6





download_instruments_csv()

get_weekly_expiry_date(index_symbol)



def my_expiry_date(*args):
    global expiry_date,exp,weekly_expiry
    exp = 1

    expiry_date = str(expiry_combo1box.get())
    print(expiry_date)


#print(weekly_expiry)
expiry_values = tk.StringVar()
expiry_combo1box = ttk.Combobox(
    root, values=weekly_expiry, width=11, textvariable=expiry_values
)
expiry_combo1box.place(x=p, y=295)
expiry_combo1box.current(0)

expiry_values.trace("w", my_expiry_date)
expiry_date = str((expiry_combo1box.get()))




def fetch_ATM(index_symbol):
    global token
    print("In fetch_ATM of:",index_symbol)
    #download_instruments_csv()
    global ATM_strike
    ATM_strike=0
    # N_atmStrike=0
    # FINN_strike=0root.after(3000, TableUI)

    if index_symbol=="BANKNIFTY":
        token = 26009
        api.subscribe(["NSE|26009"])
        print("BN")
        time.sleep(1)



        # qRes = api.get_quotes('NSE', 'Nifty Bank')
        # BN_indexLtp = float(qRes['lp'])
        BN_indexLtp = live_data[f'{token}']['ltp']
        print(BN_indexLtp)

        mod = int(BN_indexLtp)%100
        if mod < 50:
            ATM_strike =  int(math.floor(BN_indexLtp / 100)) * 100
        else:
            ATM_strike=  int(math.ceil(BN_indexLtp /100)) * 100

        if distance == 500:
            mod = int(BN_indexLtp)%500
            if mod < 250:
                ATM_strike =  int(math.floor(BN_indexLtp / 500)) * 500
            else:
                ATM_strike=  int(math.ceil(BN_indexLtp /500)) * 500

        
        #ATM_strike = 43300
        #print(get_weekly_expiry_date(index_symbol))
        setuprow(ATM_strike)
        #setuprow_hedge(ATM_strike)

    elif index_symbol=="FINNIFTY":
        token = 26037
        api.subscribe(["NSE|26037"])  
        print("FINN")
        time.sleep(1)
        # qRes = api.get_quotes('NSE', 'Nifty Fin Service')
        # FINN_indexLtp = float(qRes['lp'])

        FINN_indexLtp = live_data[f'{token}']['ltp']
        print(FINN_indexLtp)

        mod = int(FINN_indexLtp)%50
        if mod < 25:
            ATM_strike =  int(math.floor(FINN_indexLtp / 50)) * 50
        else:
            ATM_strike=  int(math.ceil(FINN_indexLtp /50)) * 50
        #ATM_strike = 20200
        #print(get_weekly_expiry_date(index_symbol))
        setuprow(ATM_strike)

    elif index_symbol=="NIFTY":
        token = 26000
        api.subscribe(["NSE|26000"])
        print("Nifty")
        time.sleep(1)



        # qRes = api.get_quotes('NSE', 'Nifty Bank')
        # BN_indexLtp = float(qRes['lp'])
        N_indexLtp = live_data[f'{token}']['ltp']
        print(N_indexLtp)

        mod = int(N_indexLtp)%50
        if mod < 50:
            ATM_strike =  int(math.floor(N_indexLtp / 50)) * 50
        else:
            ATM_strike=  int(math.ceil(N_indexLtp /50)) * 50
        
        #ATM_strike = 43300

        #print(get_weekly_expiry_date(index_symbol))

        setuprow(ATM_strike)
        #setuprow_hedge(ATM_strike)

    elif index_symbol=="MIDCPNIFTY":
        token = 26074
        api.subscribe(["NSE|26074"])
        print("MIDCPNIFTY")
        time.sleep(1)



        # qRes = api.get_quotes('NSE', 'Nifty Bank')
        # BN_indexLtp = float(qRes['lp'])
        Midcp_indexLtp = live_data[f'{token}']['ltp']
        print(Midcp_indexLtp)

        mod = int(Midcp_indexLtp)%25
        if mod < 25:
            ATM_strike =  int(math.floor(Midcp_indexLtp / 25)) * 25
        else:
            ATM_strike=  int(math.ceil(N_indexLtp /25)) * 25
        
        #ATM_strike = 43300

        setuprow(ATM_strike)
        #setuprow_hedge(ATM_strike)

    elif index_symbol=="BSXOPT":
        token = 1
        api.subscribe(["BSE|1"])
        print("SENSEX")
        time.sleep(1)



        # qRes = api.get_quotes('NSE', 'Nifty Bank')
        # BN_indexLtp = float(qRes['lp'])
        Sensex_indexLtp = live_data[f'{token}']['ltp']
        print(Sensex_indexLtp)

        mod = int(Sensex_indexLtp)%100
        if mod < 100:
            ATM_strike =  int(math.floor(Sensex_indexLtp / 100)) * 100
        else:
            ATM_strike=  int(math.ceil(Sensex_indexLtp /100)) * 100
        
        #ATM_strike = 43300

        #print(ATM_strike)

        setuprow(ATM_strike)
        #setuprow_hedge(ATM_strike)

    elif index_symbol=="BKXOPT":
        token = 12
        api.subscribe(["BSE|12"])
        print("BANKEX")
        time.sleep(1)



        # qRes = api.get_quotes('NSE', 'Nifty Bank')
        # BN_indexLtp = float(qRes['lp'])
        Bankex_indexLtp = live_data[f'{token}']['ltp']
        print(Bankex_indexLtp)

        mod = int(Bankex_indexLtp)%100
        if mod < 100:
            ATM_strike =  int(math.floor(Bankex_indexLtp / 100)) * 100
        else:
            ATM_strike=  int(math.ceil(Bankex_indexLtp /100)) * 100
        
        #ATM_strike = 54300

        #print(ATM_strike)

        setuprow(ATM_strike)
        #setuprow_hedge(ATM_strike)

    
    


feed_opened = False


live_data = {}

SYMBOLDICT = {}

global y


def event_handler_quote_update(tick_data):
    #x1= time.time()
    global live_data,token_ce, token_pe, bn_nifty_lp, nifty_lp,df,Spot_LTP,q
    #print("In event handler")
    #print(tick_data)
    if 'lp' in tick_data:
        #timest = datetime.fromtimestamp(int(tick_data['ft'])).isoformat()
        #live_data[tick_data['tk']] = {'ltp': float(tick_data['lp']) , 'tt': timest}
        live_data[tick_data['tk']] = {'ltp': float(tick_data['lp'])}
    #print(live_data)

    Spot_LTP= live_data[f'{token}']['ltp']
    ATM_strike_label["text"] = live_data[f'{token}']['ltp']


    for i in range(1,depth+2):

        token2 = str(row[i]["ce_token"])

        #print(token2)
        #print(live_data[f'{token2}']['ltp'])

        ce_ltps_labels[i-1]["text"] = live_data[f'{token2}']['ltp']

        #dis_ce[i-1]["text"] = int(live_data[f'{token1}']['ltp']) - int(row[i]['strike']) -  int(live_data[f'{token2}']['ltp'])


        token3 = str(row_PE[i]["pe_token"])
        pe_ltps_labels[i-1]["text"] = live_data[f'{token3}']['ltp']
        #print(token3)
        #print(live_data[f'{token3}']['ltp'])

    #print(live_data)


    #print("Time taken:  ",time.time()-x1)


def event_handler_order_update(tick_data):
    # print(f"Order update {tick_data}")
    #print("order update",tick_data)
    z=0


def open_callback():
    global feed_opened
    feed_opened = True


def setupwebsocket():
    global feed_opened
    api.start_websocket(
        order_update_callback=event_handler_order_update,
        subscribe_callback=event_handler_quote_update,
        socket_open_callback=open_callback,
    )
    print("websocket connected")
    sleep(1)
    while feed_opened == False:
        print(feed_opened)
        pass
    return True





def startThread(thread):  # Start the Thread (Thread Manager)
    match thread:
        case 0:
            t1 = threading.Thread(target=Login)
            t1.start()
        case 1:
            t1 = threading.Thread(target=Logout)
            t1.start()
        case 2:
            t1 = threading.Thread(target=fetch_ATM(index_symbol))
            t1.start()
        case 3:
            t1 = threading.Thread(target=0)
            t1.start()
        case 4:
            t1 = threading.Thread(target=destroy())
            t1.start()
        case 5:
            t1 = threading.Thread(target=squareoff)
            t1.start()
        case 6:
            global t2
            t2 = th.Timer(10,Refresh_LTPs)
            t2.start()
            
        case 7:
            global t3
            t3 = th.Timer(30,Refresh_qtys)
            t3.start()




def call_livedata():
    print(float(live_data[bn_TokenKey].get("lp")))
    #print(tick_data)



# def Squareoff(token,tsym,index_symbol,n):
#     if index_symbol == "MIDCPNIFTY":
#     	Squareoff_LMT(token,tsym,index_symbol,n)
#     else:
#     	Squareoff_MKT(token,tsym,index_symbol,n)


def Squareoff_MKT(token,tsym,index_symbol,n):
    global max_size,round_num,exch,qty,comp_qty,sq_po
    sq_po = fetch_positions()
    #print("squaring off ", tsym,index_symbol,n)
    try:        
        for x in range(0,len(sq_po.index)):
            # print("for loop")
            #print(sq_po.iloc[x]["tsym"])
            if sq_po.iloc[x]["tsym"] == tsym:
                #print("2",sq_po.iloc[x]["tsym"])
                qty = int(sq_po.iloc[x]["netqty"])
                comp_qty = qty
                #print("Comp Qty is",comp_qty)
                break
        
        #print(qty)
        if qty < 0 and qty!= 0:
            qty = abs(qty) * n
            #print("Before rounding",qty)
            qty = int(qty/round_num)*round_num
            #print("After",qty)
            #print("qty", qty)
            j = math.ceil(qty/max_size)
            #print("j",j)
            for i in range(0,j):
                if qty > max_size:
                    #print(f"1Exiting {max_size}",tsym)
                    api.place_order(
                    buy_or_sell="B",
                    product_type='M',
                    exchange=exch,
                    tradingsymbol=tsym,
                    quantity=max_size,
                    discloseqty=0,
                    price_type="MKT",
                    price=0,
                    trigger_price=None,
                    retention="DAY",
                    remarks="my_order_001",
                    )
                    qty=qty-max_size
                    #if index_symbol == "FINNIFTY":
                        #time.sleep(0.5)

                elif qty <= max_size:
                    #print(f"2Exiting {qty}",tsym)
                    api.place_order(
                    buy_or_sell="B",
                    product_type='M',
                    exchange=exch,
                    tradingsymbol=tsym,
                    quantity=qty,
                    discloseqty=0,
                    price_type="MKT",
                    price=0,
                    trigger_price=None,
                    retention="DAY",
                    remarks="my_order_001",
                    )
                    #if index_symbol == "FINNIFTY":
                        #time.sleep(0.5)
        elif qty > 0 and qty!= 0:
            qty = abs(qty) * n
            #print("qty", qty)
            qty = int(qty/round_num)*round_num
            j = math.ceil(qty/max_size)
            #print("j",j)
            for i in range(0,j):
                if qty > max_size:
                    #print(f"3Exiting {max_size}",tsym)
                    api.place_order(
                    buy_or_sell="S",
                    product_type='M',
                    exchange=exch,
                    tradingsymbol=tsym,
                    quantity=max_size,
                    discloseqty=0,
                    price_type="MKT",
                    price=0,
                    trigger_price=None,
                    retention="DAY",
                    remarks="my_order_001",
                    )
                    qty=qty-max_size
                    #time.sleep(0.2)

                elif qty <= max_size:
                    #print(f"4Exiting {qty}",tsym)
                    api.place_order(
                    buy_or_sell="S",
                    product_type='M',
                    exchange=exch,
                    tradingsymbol=tsym,
                    quantity=qty,
                    discloseqty=0,
                    price_type="MKT",
                    price=0,
                    trigger_price=None,
                    retention="DAY",
                    remarks="my_order_001",
                    )
                    #time.sleep(0.2)
        qty = 0

        sq_po = fetch_positions()
        Refresh_qtys_Main(sq_po)

    except Exception as e:
        #errorlog(f"an exception occurred :: {e}")
        print(e)

    #Refresh_qtys()


def Squareoff_all(t):
    global sq_po
    # if n<0 , square off short positions and if n>0 , exit short positions first then buy orders
    #print(t)
    #print("squaring off ", tsym)
    try:
        sq_po = fetch_positions()

        if t < 0:
            for x in range(0,len(sq_po.index)):
                if int(sq_po.iloc[x]["netqty"]) < 0:
                    Squareoff_MKT(int(sq_po.iloc[x]["token"]),sq_po.iloc[x]["tsym"],index_symbol,1)
                    #time.sleep(1)

            
                #time.sleep(1)

        if t > 0:
            for x in range(0,len(sq_po.index)):
                if int(sq_po.iloc[x]["netqty"]) < 0:
                    Squareoff_MKT(int(sq_po.iloc[x]["token"]),sq_po.iloc[x]["tsym"],index_symbol,1)
                    time.sleep(1)

            for x in range(0,len(sq_po.index)):
                if int(sq_po.iloc[x]["netqty"]) > 0:
                    Squareoff_MKT(int(sq_po.iloc[x]["token"]),sq_po.iloc[x]["tsym"],index_symbol,1)
                    time.sleep(1)


    except Exception as e:
        #errorlog(f"an exception occurred :: {e}")
        print(e)




def Make_API_Sell(token,tsym, qty):
    global max_size,round_num,exch,sq_po
    #print(max_size,round_num)
    #print("in API Sell")

    #print(token, "Sell ", qty)
    # print(api.get_quotes('NSE', 'Nifty Bank'))
    #print ("Sell order placed for ", tsym, " for ", qty)


    # res = api.place_order(buy_or_sell='S', product_type='M',
    #             exchange=exch, tradingsymbol=tsym,
    #             quantity=qty, discloseqty=0, price_type='MKT',
    #             retention='DAY', remarks='my_order_001')

    if index_symbol=="BANKNIFTY":
        #max_size = 90
        price=0.0

    elif index_symbol=="FINNIFTY":
        #max_size = 400
        price=0.0

    elif index_symbol=="NIFTY":
        #max_size = 50
        price=0.0

    elif index_symbol=="BKXOPT":
        #max_size = 90
        price = (live_data[f'{token}']['ltp'])*0.80
        # print("Before rounding",price)
        price = round(price/0.05) * 0.05
        price = "{:.2f}".format(price)


    qty= abs(qty)
    j = math.ceil(qty/max_size)
    
    #print("j",j)
    for i in range(0,j):
        if qty > max_size:
            #print(f"Selling {max_size}",tsym)
            api.place_order(
            buy_or_sell="S",
            product_type='M',
            exchange=exch,
            tradingsymbol=tsym,
            quantity=max_size,
            discloseqty=0,
            price_type="MKT",
            price=0,
            trigger_price=None,
            retention="DAY",
            remarks="my_order_001",
            )
            qty=qty-max_size
            #if index_symbol == "FINNIFTY":
            #time.sleep(0.5)

        elif qty <= max_size:
            #print(f"Selling {qty}",tsym)
            api.place_order(
            buy_or_sell="S",
            product_type='M',
            exchange=exch,
            tradingsymbol=tsym,
            quantity=qty,
            discloseqty=0,
            price_type="MKT",
            price=0,
            trigger_price=None,
            retention="DAY",
            remarks="my_order_001",
            )

    sq_po = fetch_positions()
    Refresh_qtys_Main(sq_po)



def Make_API_Buy(token,tsym, qty):
    global max_size,round_num,exch,sq_po
    #print(max_size,round_num)
    #print(token, "Buy ", qty)
    # print(api.get_quotes('NSE', 'Nifty Bank'))
    #print("Buy order placed for ", tsym, " for ", qty)

    j = math.ceil(qty/max_size)
    #print("j",j)
    for i in range(0,j):
        if qty > max_size:
            #print(f"Buying {max_size}",tsym)
            api.place_order(
            buy_or_sell="B",
            product_type='M',
            exchange=exch,
            tradingsymbol=tsym,
            quantity=max_size,
            discloseqty=0,
            price_type="MKT",
            price=0,
            trigger_price=None,
            retention="DAY",
            remarks="my_order_001",
            )
            qty=qty-max_size
            #if index_symbol == "FINNIFTY":
            #time.sleep(0.5)

        elif qty <= max_size:
            #print(f"Buying {qty}",tsym)
            api.place_order(
            buy_or_sell="B",
            product_type='M',
            exchange=exch,
            tradingsymbol=tsym,
            quantity=qty,
            discloseqty=0,
            price_type="MKT",
            price=0,
            trigger_price=None,
            retention="DAY",
            remarks="my_order_001",
            )
            #time.sleep(0.5)


    Refresh_qtys()


def fetch_symbolcodes(expiry_date):
    global temp_df,weekly_expiry
    print("\n\nIn fetch_symbolcodes")
    #last_spot_price = round_ltp(last_spot_price,100)
    #print("LTP is:",last_spot_price)

    instrument_df = pd.read_csv(masters)
    temp_df = instrument_df[instrument_df['Exchange']==exch]

    if exp==0:
        expiry_date = str(get_weekly_expiry_date(index_symbol))
        

    #expiry = "27-APR-2023"
    print("Expiry date is:",expiry_date)
    temp_df = temp_df.copy()
    #print(temp_df)
    temp_df = temp_df[(temp_df['Symbol']==index_symbol) & (temp_df['Expiry'] == expiry_date)]
    #print(temp_df)
    temp_df = temp_df.sort_values(by=['StrikePrice'])
    #print(temp_df)
    temp_df["StrikePrice"] = temp_df['StrikePrice'].astype(int)
    #print(temp_df)
    temp_df["StrikePrice"] = temp_df['StrikePrice'].astype(str) + temp_df["OptionType"]
    #print(temp_df)
    return temp_df



def setuprow(ATM_strike):
    print("\n\nIn setuprow ATM strike is:", ATM_strike)
    global First_strike, row, row_PE,ce_token, pe_token, lotsize_BN,index_symbol,distance
    row = {}
    row_PE = {}
    # ce_activeqty = 0
    # pe_active_qty = 0

    First_strike = 0

    #time.sleep(5)
    #BN_ATM_fn = 40800
    #print("In setuprow")
    far = int(round(depth / 2))
    #print("far:", far)
    #global First_strike, lotsize,row,row_PE
    
    #print("First strike:", First_strike)

    row_df = fetch_symbolcodes(expiry_date)
    #print(row_df)

    if index_symbol=="BANKNIFTY" or "BSXOPT" or "BKXOPT":
        First_strike = int(ATM_strike) - (distance * far)
        # print(First_strike)
        # print(depth)
        #lotsize = 15
        for i in range(1, depth+2):
            row_df2 = row_df.copy()
            #print("Row # is:", i)
            strike_main = str(First_strike + (distance * (i - 1)))
            strike_CE = str(First_strike + (distance * (i - 1))) + "CE"
            
            # print("First strike is:",strike_main)
            # print("First CE strike is:",strike_CE)
            row_df = (row_df[(row_df['StrikePrice'] == strike_CE)])
            #print(strike_CE)
            # print(row_df)
            token_CE = row_df.iloc[0]['Token']
            #print(token_CE)
            tsym_CE = row_df.iloc[0]['TradingSymbol']
            lotsize = row_df.iloc[0]['LotSize']
            #print(token_CE,",",tsym_CE)
            # print("Lot size:",lotsize)

            # print("Token CE:",token_CE)
            # print("TSYM CE:",tsym_CE)
            

            row[i] = {
                "strike": strike_main,
                "ce_strike": strike_CE,
                "ce_LTP": 0,
                "ce_token": token_CE,
                "ce_tsym": tsym_CE,
                "ce_add_qty_1": {
                    "qty": lotsize * 1 * multiplier,
                    "button_text": str(lotsize * 1 * multiplier)
                },
                "ce_add_qty_2": {
                    "qty": lotsize * 6 * multiplier,
                    "button_text": str(lotsize * 6 * multiplier)
                },
                "ce_add_qty_3": {
                    "qty": lotsize * 12 * multiplier,
                    "button_text": str(lotsize * 12 * multiplier)
                },
                "ce_buy1": {
                "qty": lotsize * 6 * multiplier,
                "button_text": str(lotsize * 6 * multiplier)
                },
                "ce_active_qty": "-",
                "ce_exit_half": {
                    "button_text": "EX-HALF"
                },
                "ce_exit_full": {
                    "button_text": "EX-FULL"
                },
                "ce_exit_partial": {
                    "button_text": "EX-1/4"
                },
                "ce_move_up": {
                "button_text": "▲"
                },
                "ce_move_down": {
                "button_text": "▼"
                },
                "Q1": 0.25,
                "Q2": 0.5,
                "Q3" : 1,
                
            }

            # print("Lot size:",lotsize)
            row_df = row_df2.copy()

            # print("Row # is:", i)
            strike_main = str(First_strike + (distance * (i - 1)))
            strike_PE = str(First_strike + (distance * (i - 1))) + "PE"
            
            # print("First strike is:",strike_PE)
            row_df = (row_df[(row_df['StrikePrice'] == strike_PE)])
            #print(strike_PE)
            # print(row_df)
            token_PE = row_df.iloc[0]['Token']
            #print(token_PE)
            tsym_PE = row_df.iloc[0]['TradingSymbol']

            # print("Token:",token_PE)
            # print("TSYM:",tsym_PE)

            row_df = row_df2.copy()

            row_PE[i] = {
                "strike": strike_main,
                "pe_strike" : strike_PE,
                "pe_LTP": 0,
                "pe_token": token_PE,
                "pe_tsym": tsym_PE,
                "pe_add_qty_1": {
                    "qty": lotsize * 1 * multiplier,
                    "button_text": str(lotsize * 1 * multiplier)
                },
                "pe_add_qty_2": {
                    "qty": lotsize * 6 * multiplier,
                    "button_text": str(lotsize * 6 * multiplier)
                },
                "pe_add_qty_3": {
                    "qty": lotsize * 12 * multiplier,
                    "button_text": str(lotsize * 12 * multiplier)
                },
                "pe_buy1": {
                    "qty": lotsize * 6 * multiplier,
                    "button_text": str(lotsize * 6 * multiplier)
                },
                "pe_active_qty": "-",
                "pe_exit_half": {
                    "button_text": "EX-HALF"
                },
                "pe_exit_full": {
                    "button_text": "EX-FULL"
                },
                "pe_exit_partial": {
                    "button_text": "EX-1/4"
                },
                "pe_move_up": {
                "button_text": "▲"
                },
                "pe_move_down": {
                "button_text": "▼"
                },
                "Q1": 0.25,
                "Q2": 0.5,
                "Q3" : 1,
            }


    if index_symbol=="NIFTY" or index_symbol=="FINNIFTY":
        for i in range(1, depth+2):
            #     if index_symbol=="NIFTY":
            #         lotsize = 25
            #     elif index_symbol=="FINNIFTY":
            #         lotsize = 40

            #ATM_strike = int(19300)

            First_strike = ATM_strike - (50 * far)
            row_df2 = row_df.copy()
            #print("Row # is:", i)
            strike_main = str(First_strike + (50 * (i - 1)))
            strike_CE = str(First_strike + (50 * (i - 1))) + "CE"
            
            #print("First strike is:",First_strike)
            row_df = (row_df[(row_df['StrikePrice'] == strike_CE)])
            #print(strike_CE)
            # print(row_df)
            token_CE = row_df.iloc[0]['Token']
            tsym_CE = row_df.iloc[0]['TradingSymbol']
            lotsize = row_df.iloc[0]['LotSize']
            # print("Lot size:",lotsize)
            #print(token_CE)
            # print("Token CE:",token_CE)
            # print("TSYM CE:",tsym_CE)
            

            row[i] = {
                "strike": strike_main,
                "ce_strike": strike_CE,
                "ce_LTP": 0,
                "ce_token": token_CE,
                "ce_tsym": tsym_CE,
                "ce_add_qty_1": {
                    "qty": lotsize * 1 * multiplier,
                    "button_text": str(lotsize * 1 * multiplier)
                },
                "ce_add_qty_2": {
                    "qty": lotsize * 6 * multiplier,
                    "button_text": str(lotsize * 6 * multiplier)
                },
                "ce_add_qty_3": {
                    "qty": lotsize * 12  * multiplier,
                    "button_text": str(lotsize * 12 * multiplier)
                },
                "ce_buy1": {
                "qty": lotsize * 24 * multiplier,
                "button_text": str(lotsize * 24 * multiplier)
                },
                "ce_active_qty": "-",
                "ce_exit_half": {
                    "button_text": "EX-HALF"
                },
                "ce_exit_full": {
                    "button_text": "EX-FULL"
                },
                "ce_exit_partial": {
                    "button_text": "EX-1/4"
                },
                "ce_move_up": {
                "button_text": "▲"
                },
                "ce_move_down": {
                    "button_text": "▼"
                },
                "Q1": 0.25,
                "Q2": 0.5,
                "Q3" : 1,
                
            }

            row_df = row_df2.copy()

            # print("Row # is:", i)
            strike_main = str(First_strike + (50 * (i - 1)))
            strike_PE = str(First_strike + (50 * (i - 1))) + "PE"
            
            # print("First strike is:",strike_PE)
            row_df = (row_df[(row_df['StrikePrice'] == strike_PE)])
            # print(strike_PE)
            # print(row_df)
            token_PE = row_df.iloc[0]['Token']
            tsym_PE = row_df.iloc[0]['TradingSymbol']

            # print("Token:",token_PE)
            # print("TSYM:",tsym_PE)

            row_df = row_df2.copy()

            row_PE[i] = {
                "strike": strike_main,
                "pe_strike" : strike_PE,
                "pe_LTP": 0,
                "pe_token": token_PE,
                "pe_tsym": tsym_PE,
                "pe_add_qty_1": {
                    "qty": lotsize * 1 * multiplier,
                    "button_text": str(lotsize * 1 * multiplier)
                },
                "pe_add_qty_2": {
                    "qty": lotsize * 6 * multiplier,
                    "button_text": str(lotsize * 6 * multiplier)
                },
                "pe_add_qty_3": {
                    "qty": lotsize * 12 * multiplier,
                    "button_text": str(lotsize * 12 * multiplier)
                },
                "pe_active_qty": "-",
                "pe_exit_half": {
                    "button_text": "EX-HALF"
                },
                "pe_exit_full": {
                    "button_text": "EX-FULL"
                },
                "pe_exit_partial": {
                    "button_text": "EX-1/4"
                },
                "pe_move_up": {
                "button_text": "▲"
                },
                "pe_move_down": {
                    "button_text": "▼"
                },
                "Q1": 1,
                "Q2": 0.5,
                "Q3" : 0.25,
                "pe_buy1": {
                "qty": lotsize * 12 * multiplier,
                "button_text": str(lotsize * 12 * multiplier)
                },
            }
    
    if index_symbol=="MIDCPNIFTY":
        for i in range(1, depth+2):
            #     if index_symbol=="NIFTY":
            #         lotsize = 25
            #     elif index_symbol=="FINNIFTY":
            #         lotsize = 40

            #ATM_strike = int(19300)

            First_strike = ATM_strike - (25 * far)
            row_df2 = row_df.copy()
            #print("Row # is:", i)
            strike_main = str(First_strike + (25 * (i - 1)))
            strike_CE = str(First_strike + (25 * (i - 1))) + "CE"
            
            #print("First strike is:",First_strike)
            row_df = (row_df[(row_df['StrikePrice'] == strike_CE)])
            #print(strike_CE)
            # print(row_df)
            token_CE = row_df.iloc[0]['Token']
            tsym_CE = row_df.iloc[0]['TradingSymbol']
            lotsize = row_df.iloc[0]['LotSize']
            # print("Lot size:",lotsize)
            #print(token_CE)
            # print("Token CE:",token_CE)
            # print("TSYM CE:",tsym_CE)
            

            row[i] = {
                "strike": strike_main,
                "ce_strike": strike_CE,
                "ce_LTP": 0,
                "ce_token": token_CE,
                "ce_tsym": tsym_CE,
                "ce_add_qty_1": {
                    "qty": lotsize * 2 * multiplier,
                    "button_text": str(lotsize * 2 * multiplier)
                },
                "ce_add_qty_2": {
                    "qty": lotsize * 4 * multiplier,
                    "button_text": str(lotsize * 4 * multiplier)
                },
                "ce_add_qty_3": {
                    "qty": lotsize * 8 * multiplier,
                    "button_text": str(lotsize * 20 * multiplier)
                },
                "ce_active_qty": "-",
                "ce_exit_half": {
                    "button_text": "EX-HALF"
                },
                "ce_exit_full": {
                    "button_text": "EX-FULL"
                },
                "ce_exit_partial": {
                    "button_text": "EX-1/4"
                },
                "Q1": 0.25,
                "Q2": 0.5,
                "Q3" : 1,
                "ce_buy1": {
                "qty": lotsize * 8 * multiplier,
                "button_text": str(lotsize * 20 * multiplier)
                },
            }

            row_df = row_df2.copy()

            # print("Row # is:", i)
            strike_main = str(First_strike + (25 * (i - 1)))
            strike_PE = str(First_strike + (25 * (i - 1))) + "PE"
            
            # print("First strike is:",strike_PE)
            row_df = (row_df[(row_df['StrikePrice'] == strike_PE)])
            # print(strike_PE)
            # print(row_df)
            token_PE = row_df.iloc[0]['Token']
            tsym_PE = row_df.iloc[0]['TradingSymbol']

            # print("Token:",token_PE)
            # print("TSYM:",tsym_PE)

            row_df = row_df2.copy()

            row_PE[i] = {
                "strike": strike_main,
                "pe_strike" : strike_PE,
                "pe_LTP": 0,
                "pe_token": token_PE,
                "pe_tsym": tsym_PE,
                "pe_add_qty_1": {
                    "qty": lotsize * 2 * multiplier,
                    "button_text": str(lotsize * 2 * multiplier)
                },
                "pe_add_qty_2": {
                    "qty": lotsize * 4 * multiplier,
                    "button_text": str(lotsize * 4 * multiplier)
                },
                "pe_add_qty_3": {
                    "qty": lotsize * 8 * multiplier,
                    "button_text": str(lotsize * 20 * multiplier)
                },
                "pe_active_qty": "-",
                "pe_exit_half": {
                    "button_text": "EX-HALF"
                },
                "pe_exit_full": {
                    "button_text": "EX-FULL"
                },
                "pe_exit_partial": {
                    "button_text": "EX-1/4"
                },
                "Q1": 1,
                "Q2": 0.5,
                "Q3" : 0.25,
                "pe_buy1": {
                "qty": lotsize * 8 * multiplier,
                "button_text": str(lotsize * 8 * multiplier)
                },
            }


    # for i in range(1, depth+2):
    #     print(row[i]["ce_tsym"])
    #     print(row_PE[i]["pe_tsym"])

    setuprow_hedge(ATM_strike,index_symbol)


def setuprow_hedge(ATM_strike,index_symbol):
    #print("\n\nIn setuprow HEDGE ATM strike is:", ATM_strike)
    global lotsize, First_strike, row_CE_hedge, row_PE_hedge,hedge_ce_token, hedge_pe_token,depth_hedge,away
    
    depth_hedge = 8
    row_CE_hedge = {}
    row_PE_hedge = {}


    #far = int(round(depth / 2))

    row_df = fetch_symbolcodes(expiry_date)

    #change
    #expiry_date = "01-MAY-2023"

    if index_symbol=="BANKNIFTY" or index_symbol=="BSXOPT" or index_symbol=="BKXOPT" :
        strike_diff = 500

        current_time = int(time.time())

        date_str = expiry_date + " 09:00"
        time_struct = time.strptime(date_str, '%d-%b-%Y %H:%M')
        unix_time = int(time.mktime(time_struct))

        date_str2 = expiry_date + " 12:30"
        time_struct2 = time.strptime(date_str2, '%d-%b-%Y %H:%M')
        unix_time2 = int(time.mktime(time_struct2))


        date_str3 = expiry_date + " 15:30"
        time_struct3 = time.strptime(date_str3, '%d-%b-%Y %H:%M')
        unix_time3 = int(time.mktime(time_struct3))

        dt = datetime.now()

        if away == 0:
            # Monday = 0 , Wed = 2, 4 = Fri, 6 = Sun
            #Fri
            if dt.weekday() == 4:
                if strike_diff==500:
                    away = 8
                else:
                    away = 20


            #Mon  
            if dt.weekday() == 0:
                if strike_diff==500:
                    away = 10
                else:
                    away = 15

            #Tue
            if dt.weekday() == 1:
                if strike_diff==500:
                    away = 6
                else:
                    away = 15

            #Wed
            if dt.weekday() == 2:
                if strike_diff==500:
                    away = 6
                else:
                    away = 15

            #Thu
            if dt.weekday() == 3:
                if strike_diff==500:
                    away = 8
                else:
                    away = 15



            print("AWAY2", away)

            if current_time > unix_time and current_time < unix_time2:
                print("Expiry day 1")
                strike_diff = 100
                away = 15
                CE_hedge_first_strike = ATM_strike + (strike_diff * away)
                PE_hedge_first_strike = ATM_strike - (strike_diff * away)

            if current_time > unix_time2 and current_time < unix_time3:
                print("Expiry day 2")
                strike_diff = 100
                away = 6
                CE_hedge_first_strike = ATM_strike + (strike_diff * away)
                PE_hedge_first_strike = ATM_strike - (strike_diff * away)
                #print("2",CE_hedge_first_strike,PE_hedge_first_strike)

            

        CE_hedge_first_strike = int(math.ceil(ATM_strike/strike_diff)*strike_diff)
        PE_hedge_first_strike = int(math.ceil(ATM_strike/strike_diff)*strike_diff)
        CE_hedge_first_strike = CE_hedge_first_strike + (strike_diff * away)
        PE_hedge_first_strike = PE_hedge_first_strike - (strike_diff * away)

        #print("1",CE_hedge_first_strike,PE_hedge_first_strike)


        print("AWAY1", away)


        for i in range(1, depth_hedge):
            row_df2 = row_df.copy()
            #print("Row # is:", i)
            #strike_main = str(First_strike + (500 * (i - 1)))
            strike_CE_hedge = str(CE_hedge_first_strike - (strike_diff * (i - 1))) + "CE"
            
            #print(strike_CE_hedge)

            row_df = (row_df[(row_df['StrikePrice'] == strike_CE_hedge)])
            #print(strike_CE)
            # print(row_df)
            token_CE = row_df.iloc[0]['Token']
            #print(token_CE)
            tsym_CE = row_df.iloc[0]['TradingSymbol']
            lotsize = row_df.iloc[0]['LotSize']
            # print("Token CE:",token_CE)
            # print("TSYM CE:",tsym_CE)
            # print("Lot size:",lotsize)

            #print(token_CE,",",tsym_CE)
            

            

            row_CE_hedge[i] = {
                "ce_strike": strike_CE_hedge,
                "ce_active_qty" : "-",
                "ce_LTP": 0,
                "ce_token": token_CE,
                "ce_tsym": tsym_CE,
                "ce_add_qty_1": {
                    "qty": lotsize * 18,
                    "button_text": str(lotsize * 18)
                },
                "ce_add_qty_2": {
                    "qty": lotsize * 36,
                    "button_text": str(lotsize * 36)
                },
                "ce_add_qty_3": {
                    "qty": lotsize * 72,
                    "button_text": str(lotsize * 72)
                },
                "ce_exit_full": {
                    "button_text": "EX-F"
                },
                "ce_exit_half": {
                    "button_text": "EX-HALF"
                },
                "ce_exit_m": {
                    "button_text": "EX-M"
                },
                "ce_move_up": {
                "button_text": "▲"
                },
                "ce_move_down": {
                "button_text": "▼"
                },
            }

            # print("Lot size:",lotsize)
            row_df = row_df2.copy()

            # print("Row # is:", i)
            strike_PE_hedge = str(PE_hedge_first_strike + (strike_diff * (i - 1))) + "PE"
            
            # print("First strike is:",strike_PE)
            row_df = (row_df[(row_df['StrikePrice'] == strike_PE_hedge)])
            # print(strike_PE)
            # print(row_df)
            token_PE = row_df.iloc[0]['Token']
            #print(token_PE)
            tsym_PE = row_df.iloc[0]['TradingSymbol']

            # print("Token:",token_PE)
            # print("TSYM:",tsym_PE)

            #print(token_PE,",",tsym_PE)


            row_df = row_df2.copy()

            row_PE_hedge[i] = { 
                "pe_strike" : strike_PE_hedge,
                "pe_active_qty": "-",
                "pe_LTP": 0,
                "pe_token": token_PE,
                "pe_tsym": tsym_PE,
                "pe_add_qty_1": {
                    "qty": lotsize * 18 ,
                    "button_text": str(lotsize * 18)
                },
                "pe_add_qty_2": {
                    "qty": lotsize * 36,
                    "button_text": str(lotsize * 36)
                },
                "pe_add_qty_3": {
                    "qty": lotsize * 72,
                    "button_text": str(lotsize * 72)
                },
                "pe_exit_full": {
                    "button_text": "EX-FULL"
                },
                "pe_exit_half": {
                    "button_text": "EX-HALF"
                },
                "pe_exit_m": {
                    "button_text": "EX-M"
                },
                "pe_move_up": {
                "button_text": "▲"
                },
                "pe_move_down": {
                "button_text": "▼"
                },
            }

    if index_symbol=="NIFTY" or index_symbol=="FINNIFTY":
        strike_diff = 50
        current_time = int(time.time())

        date_str = expiry_date + " 10:30"
        #print(date_str)
        time_struct = time.strptime(date_str, '%d-%b-%Y %H:%M')

        date_str2 = expiry_date + " 20:00"

        time_struct2 = time.strptime(date_str2, '%d-%b-%Y %H:%M')

        # Convert the struct_time object to a Unix timestamp
        unix_time = int(time.mktime(time_struct))
        unix_time2 = int(time.mktime(time_struct2))

        if away==0:
            away = 2

        if current_time > unix_time and current_time < unix_time2:
            print("Expiry Day")
            away = 0
        else:
            dt = datetime.now()
            print("Non-Expiry Day")
            # Monday = 0 , Wed = 2, 4 = Fri, 6 = Sun
            if dt.weekday() == 4:
                away = 12
            elif dt.weekday() == 0:
                away = 8
            elif dt.weekday() == 1:
                away = 3
            elif dt.weekday() == 2:
                away = 6
            elif dt.weekday() == 3:
                away = 2

        print("AWAY NIFTY/FINN",away)
                

        CE_First_strike = ATM_strike + (strike_diff * away)
        PE_First_strike = ATM_strike - (strike_diff * away)


        for i in range(1, depth_hedge):
            #
            #CE_First_strike = ATM_strike + (strike_diff * depth_hedge)
            strike_CE_hedge = str(CE_First_strike + (strike_diff * i)) + "CE"
            row_df2 = row_df.copy()
            #print("Row # is:", i)

            # print("First strike is:",strike)
            row_df = (row_df[(row_df['StrikePrice'] == strike_CE_hedge)])
            #print(strike_CE_hedge)
            # print(row_df)
            token_CE = row_df.iloc[0]['Token']
            tsym_CE = row_df.iloc[0]['TradingSymbol']
            lotsize = row_df.iloc[0]['LotSize']
            #print("Lot size:",lotsize)
            #print("Token CE:",token_CE)
            #print("TSYM CE:",tsym_CE)
            

            row_CE_hedge[i] = {
                "ce_strike": strike_CE_hedge,
                "ce_active_qty" : "-",
                "ce_LTP": 0,
                "ce_token": token_CE,
                "ce_tsym": tsym_CE,
                "ce_add_qty_1": {
                    "qty": lotsize * 18,
                    "button_text": str(lotsize * 18)
                },
                "ce_add_qty_2": {
                    "qty": lotsize * 36,
                    "button_text": str(lotsize * 36)
                },
                "ce_add_qty_3": {
                    "qty": lotsize * 72,
                    "button_text": str(lotsize * 72)
                },
                "ce_exit_full": {
                    "button_text": "EX-F"
                },
                "ce_exit_half": {
                    "button_text": "EX-HALF"
                },
                "ce_exit_m": {
                    "button_text": "EX-M"
                },
                "ce_move_up": {
                "button_text": "▲"
                },
                "ce_move_down": {
                "button_text": "▼"
                },
            }


            # print("Lot size:",lotsize)
            row_df = row_df2.copy()

            # print("Row # is:", i)
            #PE_First_strike = ATM_strike - (50 * away)
            strike_PE_hedge = str(PE_First_strike - (strike_diff * i)) + "PE"
            
            #print("First strike is:",PE_First_strike)
            row_df = (row_df[(row_df['StrikePrice'] == strike_PE_hedge)])
            # print(strike_PE)
            # print(row_df)
            token_PE = row_df.iloc[0]['Token']
            #print(token_PE)
            tsym_PE = row_df.iloc[0]['TradingSymbol']

            # print("Token:",token_PE)
            #print("TSYM:",tsym_PE)

            row_df = row_df2.copy()

            row_PE_hedge[i] = {
                "pe_strike" : strike_PE_hedge,
                "pe_active_qty": "-",
                "pe_LTP": 0,
                "pe_token": token_PE,
                "pe_tsym": tsym_PE,
                "pe_add_qty_1": {
                    "qty": lotsize * 18 ,
                    "button_text": str(lotsize * 18)
                },
                "pe_add_qty_2": {
                    "qty": lotsize * 36,
                    "button_text": str(lotsize * 36)
                },
                "pe_add_qty_3": {
                    "qty": lotsize * 72,
                    "button_text": str(lotsize * 72)
                },
                "pe_exit_full": {
                    "button_text": "EX-FULL"
                },
                "pe_exit_half": {
                    "button_text": "EX-HALF"
                },
                "pe_exit_m": {
                    "button_text": "EX-M"
                },
                "pe_move_up": {
                "button_text": "▲"
                },
                "pe_move_down": {
                "button_text": "▼"
                },
            }
    if index_symbol=="MIDCPNIFTY":
        strike_diff = 25
        current_time = int(time.time())

        date_str = expiry_date + " 10:30"
        #print(date_str)
        time_struct = time.strptime(date_str, '%d-%b-%Y %H:%M')

        date_str2 = expiry_date + " 20:00"

        time_struct2 = time.strptime(date_str2, '%d-%b-%Y %H:%M')

        # Convert the struct_time object to a Unix timestamp
        unix_time = int(time.mktime(time_struct))
        unix_time2 = int(time.mktime(time_struct2))

        away = 16

        if current_time > unix_time and current_time < unix_time2:
            print("Success6")
            away = 10
        else:
            dt = datetime.now()
            # Monday = 0 , Wed = 2, 4 = Fri, 6 = Sun
            if dt.weekday() == 4:
                away = 14
            elif dt.weekday() == 0:
                away = 14
            elif dt.weekday() == 1:
                away = 8

        CE_First_strike = ATM_strike + (strike_diff * away)
        PE_First_strike = ATM_strike - (strike_diff * away)


        for i in range(1, depth_hedge):
            #
            #CE_First_strike = ATM_strike + (strike_diff * depth_hedge)
            strike_CE_hedge = str(CE_First_strike - (strike_diff * i)) + "CE"
            row_df2 = row_df.copy()
            #print("Row # is:", i)

            # print("First strike is:",strike)
            row_df = (row_df[(row_df['StrikePrice'] == strike_CE_hedge)])
            #print(strike_CE_hedge)
            # print(row_df)
            token_CE = row_df.iloc[0]['Token']
            tsym_CE = row_df.iloc[0]['TradingSymbol']
            lotsize = row_df.iloc[0]['LotSize']
            #print("Lot size:",lotsize)
            #print("Token CE:",token_CE)
            #print("TSYM CE:",tsym_CE)
            

            row_CE_hedge[i] = {
                "ce_strike": strike_CE_hedge,
                "ce_active_qty" : "-",
                "ce_LTP": 0,
                "ce_token": token_CE,
                "ce_tsym": tsym_CE,
                "ce_add_qty_1": {
                    "qty": lotsize * 36,
                    "button_text": str(lotsize * 36)
                },
                "ce_add_qty_2": {
                    "qty": lotsize * 60,
                    "button_text": str(lotsize * 60)
                },
                "ce_exit_full": {
                    "button_text": "EX-F"
                },
                "ce_exit_half": {
                    "button_text": "EX-HALF"
                },
                "ce_exit_m": {
                    "button_text": "EX-M"
                },
                "ce_move_up": {
                "button_text": "▲"
                },
                "ce_move_down": {
                "button_text": "▼"
                },
            }

            # print("Lot size:",lotsize)
            row_df = row_df2.copy()

            # print("Row # is:", i)
            #PE_First_strike = ATM_strike - (50 * away)
            strike_PE_hedge = str(PE_First_strike + (strike_diff * i)) + "PE"
            
            #print("First strike is:",PE_First_strike)
            row_df = (row_df[(row_df['StrikePrice'] == strike_PE_hedge)])
            # print(strike_PE)
            # print(row_df)
            token_PE = row_df.iloc[0]['Token']
            #print(token_PE)
            tsym_PE = row_df.iloc[0]['TradingSymbol']

            # print("Token:",token_PE)
            #print("TSYM:",tsym_PE)

            row_df = row_df2.copy()

            row_PE_hedge[i] = {
                "pe_strike" : strike_PE_hedge,
                "pe_active_qty": "-",
                "pe_LTP": 0,
                "pe_token": token_PE,
                "pe_tsym": tsym_PE,
                "pe_add_qty_1": {
                    "qty": lotsize * 36 ,
                    "button_text": str(lotsize * 36)
                },
                "pe_add_qty_2": {
                    "qty": lotsize * 60,
                    "button_text": str(lotsize * 60)
                },
                "pe_exit_full": {
                    "button_text": "EX-FULL"
                },
                "pe_exit_half": {
                    "button_text": "EX-HALF"
                },
                "pe_exit_m": {
                    "button_text": "EX-M"
                },
                "pe_move_up": {
                "button_text": "▲"
                },
                "pe_move_down": {
                "button_text": "▼"
                },
            }

    

    subscribe()

    TableUI()


def Move_up_strike_ce(token,tsym):
    global row,row_PE,qty,comp_qty,sq_po

    #sq_po = fetch_positions()
    comp_qty=0
    #print("in move up ce strike")

    for x in range(0,len(sq_po.index)):
        if sq_po.iloc[x]["tsym"] == tsym:
            comp_qty = int(sq_po.iloc[x]["netqty"])
            #print("Comp Qty is",comp_qty,tsym)

    if comp_qty<0:
            for i in range(1, depth+2):
                if row[i]["ce_tsym"]==tsym:
                    Squareoff_MKT(token,tsym,index_symbol,1)
                    Make_API_Sell(int(row[i-1]["ce_token"]),row[i-1]["ce_tsym"],comp_qty)
                    break
        
    else:
        for i in range(1, depth_hedge):
            if row_CE_hedge[i]["ce_tsym"]==tsym:
                Make_API_Buy(int(row_CE_hedge[i-1]["ce_token"]),row_CE_hedge[i-1]["ce_tsym"],comp_qty)
                Squareoff_MKT(token,tsym,index_symbol,1)
                break


def Move_down_strike_ce(token,tsym):
    global row,row_PE,qty,comp_qty,sq_po

    #sq_po = fetch_positions()
    comp_qty=0
    #print("in move up ce strike")

    for x in range(0,len(sq_po.index)):
        if sq_po.iloc[x]["tsym"] == tsym:
            comp_qty = int(sq_po.iloc[x]["netqty"])
            #print("Comp Qty is",comp_qty,tsym)

    if comp_qty<0:
            for i in range(1, depth+2):
                if row[i]["ce_tsym"]==tsym:
                    Squareoff_MKT(token,tsym,index_symbol,1)
                    Make_API_Sell(int(row[i+1]["ce_token"]),row[i+1]["ce_tsym"],comp_qty)
                    break
        
    else:
        for i in range(1, depth_hedge):
            if row_CE_hedge[i]["ce_tsym"]==tsym:
                Make_API_Buy(int(row_CE_hedge[i+1]["ce_token"]),row_CE_hedge[i+1]["ce_tsym"],comp_qty)
                Squareoff_MKT(token,tsym,index_symbol,1)
                break

def Move_up_strike_pe(token,tsym):
    global row,row_PE,qty,comp_qty,sq_po

    #sq_po = fetch_positions()
    comp_qty=0
    #print("in move up PE strike")

    for x in range(0,len(sq_po.index)):
        if sq_po.iloc[x]["tsym"] == tsym:
            comp_qty = int(sq_po.iloc[x]["netqty"])
            print("Comp Qty is",comp_qty,tsym)
            break

    if comp_qty<0:
            for i in range(1, depth+2):
                if row_PE[i]["pe_tsym"]==tsym:
                    Squareoff_MKT(token,tsym,index_symbol,1)
                    Make_API_Sell(int(row_PE[i-1]["pe_token"]),row_PE[i-1]["pe_tsym"],comp_qty)
                    break
        
    else:
        for i in range(1, depth_hedge):
            if row_PE_hedge[i]["pe_tsym"]==tsym:
                Make_API_Buy(int(row_PE_hedge[i-1]["pe_token"]),row_PE_hedge[i-1]["pe_tsym"],comp_qty)
                Squareoff_MKT(token,tsym,index_symbol,1)
                break


def Move_down_strike_pe(token,tsym):
    global row,row_PE,qty,comp_qty,sq_po

    #sq_po = fetch_positions()
    comp_qty=0
    #print("in move down PE strike")

    for x in range(0,len(sq_po.index)):
        if sq_po.iloc[x]["tsym"] == tsym:
            comp_qty = int(sq_po.iloc[x]["netqty"])
            #print("Comp Qty is",comp_qty,tsym)
            break

    if comp_qty<0:
            for i in range(1, depth+2):
                if row_PE[i]["pe_tsym"]==tsym:
                    Squareoff_MKT(token,tsym,index_symbol,1)
                    Make_API_Sell(int(row_PE[i+1]["pe_token"]),row_PE[i+1]["pe_tsym"],comp_qty)
                    break
        
    else:
        for i in range(1, depth_hedge):
            if row_PE_hedge[i]["pe_tsym"]==tsym:
                Make_API_Buy(int(row_PE_hedge[i+1]["pe_token"]),row_PE_hedge[i+1]["pe_tsym"],comp_qty)
                Squareoff_MKT(token,tsym,index_symbol,1)
                break


global labels
labels = []
ce_ltps_labels = []
pe_ltps_labels = []
ce_qty_labels = []
pe_qty_labels = []
ce_hedge_qty_labels = []
pe_hedge_qty_labels = []
ce_hedge_ltps_labels = []
pe_hedge_ltps_labels = []

# create table headers
def TableUI():
    s=1
    destroy()
    headers = ["CE1", "CE2", "CE3", "EP", "EH","EF","MO-U", "Qty", "MO-D","Buy","LTP", "Strikes", "LTP","Buy","MO-U", "Qty", "MO-D","EF", "EH", "EP", "PE3", "PE2", "PE1"]
    for col, header in enumerate(headers):
        label1 = ttk.Label(root, text=header, background="#808080" , font=("Arial", 10, "bold"), anchor="center", width=6)
        label1.grid(row=0, column=col, padx=5, pady=1)
        labels.append(label1)



    ###create table rows
    for i in range(1, depth+2):

        t = (depth+2)/2

        global ce_active_qty,pe_active_qty,away
        #print(depth)
        #print("In Table UI")

        ####### CE side Main ######

        add_qty_btn1 = ttk.Button(root, text=row[i]["ce_add_qty_1"]["button_text"],width=6,
                                 command=lambda ce_token = row[i]["ce_token"],ce_tsym = row[i]["ce_tsym"], qty = row[i]["ce_add_qty_1"]["qty"]: Make_API_Sell(ce_token,ce_tsym, qty))
        add_qty_btn1.grid(row=i, column=0, padx=5, pady=1)
        labels.append(add_qty_btn1)


        add_qty_btn2 = ttk.Button(root, text=row[i]["ce_add_qty_2"]["button_text"],width=6,
                                 command=lambda ce_token = row[i]["ce_token"],ce_tsym = row[i]["ce_tsym"], qty = row[i]["ce_add_qty_2"]["qty"]: Make_API_Sell(ce_token,ce_tsym, qty))
        add_qty_btn2.grid(row=i, column=1, padx=5, pady=1)
        labels.append(add_qty_btn2)


        add_qty_btn3 = ttk.Button(root, text=row[i]["ce_add_qty_3"]["button_text"],width=6,
                                 command=lambda ce_token = row[i]["ce_token"],ce_tsym = row[i]["ce_tsym"], qty = row[i]["ce_add_qty_3"]["qty"]: Make_API_Sell(ce_token,ce_tsym, qty))
        add_qty_btn3.grid(row=i, column=2, padx=5, pady=1)
        labels.append(add_qty_btn3)



        exit_qty_btn1 = ttk.Button(root, text=row[i]["ce_exit_partial"]["button_text"], width=8,
                                  command=lambda ce_token = row[i]["ce_token"],ce_tsym = row[i]["ce_tsym"], qty = row[i]["Q1"]: Squareoff_MKT(ce_token,ce_tsym,index_symbol,qty))
        exit_qty_btn1.grid(row=i, column=3, padx=5, pady=1)
        labels.append(exit_qty_btn1)



        exit_qty_btn2 = ttk.Button(root, text=row[i]["ce_exit_half"]["button_text"],width=8,
                                  command=lambda ce_token = row[i]["ce_token"],ce_tsym = row[i]["ce_tsym"], qty = row[i]["Q2"]: Squareoff_MKT(ce_token,ce_tsym,index_symbol,qty))
        exit_qty_btn2.grid(row=i, column=4, padx=5, pady=1)
        labels.append(exit_qty_btn2)


        exit_qty_btn3 = ttk.Button(root, text=row[i]["ce_exit_full"]["button_text"],width=8,
                                  command= lambda ce_token = row[i]["ce_token"],ce_tsym = row[i]["ce_tsym"] , qty = row[i]["Q3"]: Squareoff_MKT(ce_token,ce_tsym,index_symbol,qty))
        exit_qty_btn3.grid(row=i, column=5, padx=5, pady=1)
        labels.append(exit_qty_btn3)



        move_up_btn1 = ttk.Button(root, text=row[i]["ce_move_up"]["button_text"],width=6,
                                 command=lambda ce_token = row[i]["ce_token"],ce_tsym = row[i]["ce_tsym"]: Move_up_strike_ce(ce_token,ce_tsym))
        move_up_btn1.grid(row=i, column=6, padx=5, pady=1)



        ce_active_qty1 = ttk.Label(root, text=row[i]["ce_active_qty"],background="#808080",font=("Arial", 10, "normal"))
        labels.append(ce_active_qty1)
        ce_active_qty1.grid(row=i, column=7, padx=5, pady=1)
        ce_qty_labels.append(ce_active_qty1)

        #print(i , row[i]["ce_active_qty"])



        move_down_btn1 = ttk.Button(root, text=row[i]["ce_move_down"]["button_text"],width=6,
                                 command=lambda ce_token = row[i]["ce_token"],ce_tsym = row[i]["ce_tsym"]: Move_down_strike_ce(ce_token,ce_tsym))
        move_down_btn1.grid(row=i, column=8, padx=5, pady=1)



        buy_qty_button1  =ttk.Button(root, text=row[i]["ce_buy1"]["button_text"],width=6,
                                  command= lambda ce_token = row[i]["ce_token"],ce_tsym = row[i]["ce_tsym"] , qty = row[i]["ce_buy1"]["qty"]: Make_API_Buy(ce_token,ce_tsym, qty))

        buy_qty_button1.grid(row=i, column=9, padx=5, pady=1)
        labels.append(buy_qty_button1)



        CE_Ltp1 = ttk.Label(root, text=row[i]["ce_LTP"],background="#808080",font=("Arial", 10, "normal"))
        #CE_Ltp1.config(bg="#808080")
        CE_Ltp1.grid(row=i, column=10, padx=6, pady=1)
        labels.append(CE_Ltp1)
        ce_ltps_labels.append(CE_Ltp1)



        if i ==t:
            Strikes = ttk.Label(root, text=row[i]["strike"], background="#801180",font=("Arial", 11, "bold"))
            Strikes.grid(row=i, column=11, padx=5, pady=1)
            labels.append(Strikes)
        else:
            Strikes = ttk.Label(root, text=row[i]["strike"], background="#808080",font=("Arial", 11, "bold"))
            Strikes.grid(row=i, column=11, padx=5, pady=1)
            labels.append(Strikes)







        ####### PE side Main ######

        pe_Ltp1 = ttk.Label(root, text=row_PE[i]["pe_LTP"],background="#808080", font=("Arial", 10, "normal"))
        pe_Ltp1.grid(row=i, column=12, padx=5, pady=1)
        labels.append(pe_Ltp1)
        pe_ltps_labels.append(pe_Ltp1)

        #pe_active_qty = ttk.Label(root, text="#######", font=("Arial", 10, "normal"))
        #pe_active_qty.destroy()

        buy_qty_button2 = ttk.Button(root, text=row_PE[i]["pe_buy1"]["button_text"],width=6,
                                  command= lambda pe_token = row_PE[i]["pe_token"],pe_tsym = row_PE[i]["pe_tsym"] , qty = row_PE[i]["pe_buy1"]["qty"]: Make_API_Buy(pe_token,pe_tsym, qty))
        buy_qty_button2.grid(row=i, column=13, padx=5, pady=1)
        labels.append(buy_qty_button2)

        move_up_btn2 = ttk.Button(root, text=row_PE[i]["pe_move_up"]["button_text"],width=6,
                                 command=lambda pe_token = row_PE[i]["pe_token"],pe_tsym = row_PE[i]["pe_tsym"]: Move_up_strike_pe(pe_token,pe_tsym))
        move_up_btn2.grid(row=i, column=14, padx=5, pady=1)



        pe_active_qty1 = ttk.Label(root, text=row_PE[i]["pe_active_qty"], background="#808080",font=("Arial", 10, "normal"))
        pe_active_qty1.grid(row=i, column=15, padx=5, pady=1)
        labels.append(pe_active_qty1)
        pe_qty_labels.append(pe_active_qty1)


        move_down_btn2 = ttk.Button(root, text=row_PE[i]["pe_move_down"]["button_text"],width=6,
                                 command=lambda pe_token = row_PE[i]["pe_token"],pe_tsym = row_PE[i]["pe_tsym"]: Move_down_strike_pe(pe_token,pe_tsym))
        move_down_btn2.grid(row=i, column=16, padx=5, pady=1)




        
        exit_qty_btn4 = ttk.Button(root, text=row_PE[i]["pe_exit_full"]["button_text"], width=7,
                                  command=lambda pe_token =row_PE[i]["pe_token"], pe_tsym = row_PE[i]["pe_tsym"],qty = 1 : Squareoff_MKT(pe_token,pe_tsym,index_symbol,qty))
        exit_qty_btn4.grid(row=i, column=17, padx=5, pady=1)
        labels.append(exit_qty_btn4)


        exit_qty_btn5 = ttk.Button(root, text=row_PE[i]["pe_exit_half"]["button_text"], width=7,
                                  command=lambda pe_token =row_PE[i]["pe_token"], pe_tsym = row_PE[i]["pe_tsym"],qty = 0.5 : Squareoff_MKT(pe_token,pe_tsym,index_symbol,qty))
        exit_qty_btn5.grid(row=i, column=18, padx=5, pady=1)
        labels.append(exit_qty_btn5)


        exit_qty_btn6 = ttk.Button(root, text=row_PE[i]["pe_exit_partial"]["button_text"], width=7,
                                  command=lambda pe_token =row_PE[i]["pe_token"], pe_tsym = row_PE[i]["pe_tsym"],qty = 0.25 : Squareoff_MKT(pe_token,pe_tsym,index_symbol,qty))
        exit_qty_btn6.grid(row=i, column=19, padx=5, pady=1)
        labels.append(exit_qty_btn6)



        add_qty_btn4 = ttk.Button(root, text=row_PE[i]["pe_add_qty_3"]["button_text"],width=6,
                                 command=lambda pe_token=row_PE[i]["pe_token"], pe_tsym = row_PE[i]["pe_tsym"], qty = row_PE[i]["pe_add_qty_3"]["qty"]: Make_API_Sell(pe_token,pe_tsym, qty))
        add_qty_btn4.grid(row=i, column=20, padx=5, pady=1)
        labels.append(add_qty_btn4)
        

        add_qty_btn5 = ttk.Button(root, text=row_PE[i]["pe_add_qty_2"]["button_text"],width=6,
                                  command=lambda pe_token=row_PE[i]["pe_token"], pe_tsym = row_PE[i]["pe_tsym"], qty = row_PE[i]["pe_add_qty_2"]["qty"]: Make_API_Sell(pe_token,pe_tsym, qty))
        add_qty_btn5.grid(row=i, column=21, padx=5, pady=1)
        labels.append(add_qty_btn5)


        add_qty_btn6 = ttk.Button(root, text=row_PE[i]["pe_add_qty_1"]["button_text"],width=6,
                                  command=lambda pe_token=row_PE[i]["pe_token"], pe_tsym = row_PE[i]["pe_tsym"], qty = row_PE[i]["pe_add_qty_1"]["qty"]: Make_API_Sell(pe_token,pe_tsym, qty))
        add_qty_btn6.grid(row=i, column=22, padx=5, pady=1)
        labels.append(add_qty_btn6)

    #print(i)

    #print(labels)
    k = i + 1
    #root.update()


    Separator = ttk.Label(root, text=".", background="#808080",font=("Arial", 10, "normal"))
    Separator.grid(row=k, column=0, padx=5, pady=1)
    labels.append(Separator)

    #def TableUI_Hedge():
    #destroy()
    #print(k)
    headers2 = [ "CE","MO-D","Qty","MO-U" , "LTP","Add1","Add2","Add3","EF","EH", "EM" , "||", "PE","MO-D","Qty","MO-U","LTP","Add1","Add2","Add3","EF","EH" ,"EM"]
    for col, header in enumerate(headers2):
        label2 = ttk.Label(root, text=header, background="#808080",font=("Arial", 10, "bold"), anchor="center",width=6)
        label2.grid(row=k+1, column=col, padx=5, pady=1)
        labels.append(label2)

    ###### CE side HEDGE ######

    ##create table rows

    x = 0
    for j in range(1, depth_hedge):

        # global ce_active_qty,pe_active_qty,CE_Ltp,pe_Ltp
        #print(depth)
        #print("In Table UI")

        ####### CE side ######

        CE_Strikes = ttk.Label(root, text=row_CE_hedge[j]["ce_strike"],background="#808080", font=("Arial", 10, "bold"))
        CE_Strikes.grid(row=k+j+1, column=0, padx=5, pady=1)
        labels.append(CE_Strikes)

        move_up_btn3 = ttk.Button(root, text=row_CE_hedge[j]["ce_move_up"]["button_text"],width=6,
                                 command=lambda ce_token = row_CE_hedge[j]["ce_token"],ce_tsym = row_CE_hedge[j]["ce_tsym"]: Move_up_strike_ce(ce_token,ce_tsym))
        move_up_btn3.grid(row=k+j+1, column=1, padx=5, pady=1)


        ce_qty = ttk.Label(root, text=row_CE_hedge[j]["ce_active_qty"],background="#808080", font=("Arial", 10, "normal"))
        ce_qty.grid(row=k+j+1, column=2, padx=5, pady=1)
        labels.append(ce_qty)
        ce_hedge_qty_labels.append(ce_qty)


        move_down_btn3 = ttk.Button(root, text=row_CE_hedge[j]["ce_move_down"]["button_text"],width=6,
                                 command=lambda ce_token = row_CE_hedge[j]["ce_token"],ce_tsym = row_CE_hedge[j]["ce_tsym"]: Move_down_strike_ce(ce_token,ce_tsym))
        move_down_btn3.grid(row=k+j+1, column=3, padx=5, pady=1)




        CE_LTP_hedge = ttk.Label(root, text=row_CE_hedge[j]["ce_LTP"],background="#808080", font=("Arial", 10, "normal"))
        CE_LTP_hedge.grid(row=k+j+1, column=4, padx=5, pady=1)
        labels.append(CE_LTP_hedge)
        ce_hedge_ltps_labels.append(CE_LTP_hedge)

        add_ce_qty_btn_hedge = ttk.Button(root, text=row_CE_hedge[j]["ce_add_qty_1"]["button_text"],width=6,
                                 command=lambda ce_token =row_CE_hedge[j]["ce_token"], ce_tsym = row_CE_hedge[j]["ce_tsym"], qty = row_CE_hedge[j]["ce_add_qty_1"]["qty"]: Make_API_Buy(ce_token,ce_tsym, qty))
        add_ce_qty_btn_hedge.grid(row=k+j+1, column=5, padx=5, pady=1)



        add_ce_qty_btn_hedge2 = ttk.Button(root, text=row_CE_hedge[j]["ce_add_qty_2"]["button_text"],width=6,
                                 command=lambda ce_token =row_CE_hedge[j]["ce_token"], ce_tsym = row_CE_hedge[j]["ce_tsym"], qty = row_CE_hedge[j]["ce_add_qty_2"]["qty"]: Make_API_Buy(ce_token,ce_tsym, qty))
        add_ce_qty_btn_hedge2.grid(row=k+j+1, column=6, padx=5, pady=1)


        add_ce_qty_btn_hedge3 = ttk.Button(root, text=row_CE_hedge[j]["ce_add_qty_3"]["button_text"],width=6,
                                 command=lambda ce_token =row_CE_hedge[j]["ce_token"], ce_tsym = row_CE_hedge[j]["ce_tsym"], qty = row_CE_hedge[j]["ce_add_qty_3"]["qty"]: Make_API_Buy(ce_token,ce_tsym, qty))
        add_ce_qty_btn_hedge3.grid(row=k+j+1, column=7, padx=5, pady=1)


        ce_exit_qty_btn_hedge= ttk.Button(root, text=row_CE_hedge[j]["ce_exit_full"]["button_text"],width=6,
                                  command=lambda ce_token =row_CE_hedge[j]["ce_token"], ce_tsym = row_CE_hedge[j]["ce_tsym"]: Squareoff_MKT(ce_token,ce_tsym,index_symbol,1))
        ce_exit_qty_btn_hedge.grid(row=k+j+1, column=8, padx=5, pady=1)


        ce_exit_qty_btn_hedge2= ttk.Button(root, text=row_CE_hedge[j]["ce_exit_half"]["button_text"],width=6,
                                  command=lambda ce_token =row_CE_hedge[j]["ce_token"],ce_tsym = row_CE_hedge[j]["ce_tsym"]: Squareoff_MKT(ce_token,ce_tsym,index_symbol,0.5))
        ce_exit_qty_btn_hedge2.grid(row=k+j+1, column=9, padx=5, pady=1)

        ce_exit_qty_btn_hedge3= ttk.Button(root, text=row_CE_hedge[j]["ce_exit_m"]["button_text"],width=6,
                                  command=lambda ce_token =row_CE_hedge[j]["ce_token"],ce_tsym = row_CE_hedge[j]["ce_tsym"]: Squareoff_MKT(ce_token,ce_tsym,index_symbol,0.1))
        ce_exit_qty_btn_hedge3.grid(row=k+j+1, column=10, padx=5, pady=1)


        middle_hedge = ttk.Label(root, text="||", background="#808080",font=("Arial", 10, "normal"))
        middle_hedge.grid(row=k+j+1, column=11, padx=5, pady=1)
        labels.append(middle_hedge)



        ####### PE side HEDGE ######


        PE_Strikes_hedge= ttk.Label(root, text=row_PE_hedge[j]["pe_strike"], background="#808080",font=("Arial", 10, "bold"))
        PE_Strikes_hedge.grid(row=k+j+1, column=12, padx=5, pady=1)
        labels.append(PE_Strikes_hedge)

        move_up_btn4 = ttk.Button(root, text=row_PE_hedge[j]["pe_move_up"]["button_text"],width=6,
                                 command=lambda pe_token = row_PE_hedge[j]["pe_token"],pe_tsym = row_PE_hedge[j]["pe_tsym"]: Move_up_strike_pe(pe_token,pe_tsym))
        move_up_btn4.grid(row=k+j+1, column=13, padx=5, pady=1)


        pe_qty = ttk.Label(root, text=row_PE_hedge[j]["pe_active_qty"],background="#808080", font=("Arial", 10, "normal"))
        pe_qty.grid(row=k+j+1, column=14, padx=5, pady=1)
        labels.append(pe_qty)
        pe_hedge_qty_labels.append(pe_qty)


        move_down_btn4 = ttk.Button(root, text=row_PE_hedge[j]["pe_move_down"]["button_text"],width=6,
                                 command=lambda pe_token = row_PE_hedge[j]["pe_token"],pe_tsym = row_PE_hedge[j]["pe_tsym"]: Move_down_strike_pe(pe_token,pe_tsym))
        move_down_btn4.grid(row=k+j+1, column=15, padx=5, pady=1)



        PE_LTP_hedge = ttk.Label(root, text=row_PE_hedge[j]["pe_LTP"], background="#808080",font=("Arial", 10, "normal"))
        PE_LTP_hedge.grid(row=k+j+1, column=16, padx=5, pady=1)
        labels.append(PE_LTP_hedge)
        pe_hedge_ltps_labels.append(PE_LTP_hedge)


        add_qty_btn_hedge = ttk.Button(root, text=row_PE_hedge[j]["pe_add_qty_1"]["button_text"],width=6,
                                 command=lambda pe_token =row_PE_hedge[j]["pe_token"], pe_tsym = row_PE_hedge[j]["pe_tsym"], qty = row_PE_hedge[j]["pe_add_qty_1"]["qty"]: Make_API_Buy(pe_token,pe_tsym, qty))
        add_qty_btn_hedge.grid(row=k+j+1, column=17, padx=5, pady=1)


        add_qty_btn_hedge2 = ttk.Button(root, text=row_PE_hedge[j]["pe_add_qty_2"]["button_text"],width=6,
                                 command=lambda pe_token =row_PE_hedge[j]["pe_token"], pe_tsym = row_PE_hedge[j]["pe_tsym"], qty = row_PE_hedge[j]["pe_add_qty_2"]["qty"]: Make_API_Buy(pe_token,pe_tsym, qty))
        add_qty_btn_hedge2.grid(row=k+j+1, column=18, padx=5, pady=1)


        add_qty_btn_hedge3 = ttk.Button(root, text=row_PE_hedge[j]["pe_add_qty_3"]["button_text"],width=6,
                                 command=lambda pe_token =row_PE_hedge[j]["pe_token"], pe_tsym = row_PE_hedge[j]["pe_tsym"], qty = row_PE_hedge[j]["pe_add_qty_3"]["qty"]: Make_API_Buy(pe_token,pe_tsym, qty))
        add_qty_btn_hedge3.grid(row=k+j+1, column=19, padx=5, pady=1)

        
        PE_exit_qty_btn_hedge= ttk.Button(root, text=row_PE_hedge[j]["pe_exit_full"]["button_text"],width=6,
                                  command=lambda pe_token =row_PE_hedge[j]["pe_token"], pe_tsym = row_PE_hedge[j]["pe_tsym"]: Squareoff_MKT(pe_token,pe_tsym,index_symbol,1))
        PE_exit_qty_btn_hedge.grid(row=k+j+1, column=20, padx=5, pady=1)


        PE_exit_qty_btn_hedge2= ttk.Button(root, text=row_PE_hedge[j]["pe_exit_half"]["button_text"],width=6,
                                  command=lambda pe_token =row_PE_hedge[j]["pe_token"],pe_tsym = row_PE_hedge[j]["pe_tsym"]: Squareoff_MKT(pe_token,pe_tsym,index_symbol,0.5))
        PE_exit_qty_btn_hedge2.grid(row=k+j+1, column=21, padx=5, pady=1)


        PE_exit_qty_btn_hedge3= ttk.Button(root, text=row_PE_hedge[j]["pe_exit_m"]["button_text"],width=6,
                                  command=lambda pe_token =row_PE_hedge[j]["pe_token"],pe_tsym = row_PE_hedge[j]["pe_tsym"]: Squareoff_MKT(pe_token,pe_tsym,index_symbol,0.10))
        PE_exit_qty_btn_hedge3.grid(row=k+j+1, column=22, padx=5, pady=1)

    #root.update()
    #root.after(3000, TableUI)


def subscribe():

    global row,row_PE,row_PE_hedge,row_CE_hedge,exch

    if index_symbol == "BSXOPT" or index_symbol == "BKXOPT":
        exch = "BFO"
    else:
        exch = "NFO"

    print("IN subscribe")
    for i in range(1, depth+2):
        ce = row[i]["ce_token"]
        #print(row[i]["ce_tsym"],row[i]["ce_token"])
        ce_tokens = f"{exch}|{ce}"
        #print(ce_tokens)
        r = api.subscribe(ce_tokens)
        #print("sub", r)

    #time.sleep(3)

    for i in range(1, depth+2):
        pe = row_PE[i]["pe_token"]
        #print(row_PE[i]["pe_tsym"],row_PE[i]["pe_token"])
        pe_tokens = f"{exch}|{pe}"
        #print(pe_tokens)
        api.subscribe(pe_tokens)
    #time.sleep(3)

    for i in range(1, depth_hedge):
        ce = row_CE_hedge[i]["ce_token"]
        #print(row_CE_hedge[i]["ce_tsym"],row_CE_hedge[i]["ce_token"])
        ce_tokens = f"{exch}|{ce}"
        #print("hedges ce",ce_tokens)
        api.subscribe(ce_tokens)
    #time.sleep(3)

    for i in range(1, depth_hedge):
        pe = row_PE_hedge[i]["pe_token"]
        #print(row_PE_hedge[i]["pe_tsym"],row_PE_hedge[i]["pe_token"])
        pe_tokens = f"{exch}|{pe}"
        api.subscribe(pe_tokens)
        #print("hedges pe",pe_tokens)
    #time.sleep(3)
    #print("Ending subscribe")


    #time.sleep(3)
    print("Ending subscribe")


def destroy():
    #print("In Destroy")
    for label in labels:
        #print(label)
        label.destroy()
    labels.clear()
    #print(labels)




def Refresh_LTPs():

    #print("in Refresh_LTPs",datetime.now())

    # for i in range(1, depth+2):
    #     token = str(row[i]["ce_token"])
    #     row[i]["ce_LTP"] = live_data[f'{token}']['ltp']

    # for i in range(1, depth+2):
    #     token = str(row_PE[i]["pe_token"])
    #     row_PE[i]["pe_LTP"] = live_data[f'{token}']['ltp']

    # for i in range(1, depth_hedge):
    #     print(row_CE_hedge[i]["ce_tsym"],row_CE_hedge[i]["ce_token"])
    #     print(row_PE_hedge[i]["pe_tsym"],row_PE_hedge[i]["pe_token"])


    for i in range(1, depth_hedge):

        token4 = str(row_CE_hedge[i]["ce_token"])
        ce_hedge_ltps_labels[i-1]["text"] = live_data[f'{token4}']['ltp']


    for i in range(1, depth_hedge):
        token4 = str(row_PE_hedge[i]["pe_token"])
        pe_hedge_ltps_labels[i-1]["text"] = live_data[f'{token4}']['ltp']

    #destroy()
    #TableUI()
    #print("in Ending LTPs",datetime.now())

def fetch_positions():
    global sq_po
    #print("In Fetch positions")
    sq_po = api.get_positions()
    #print(sq_po)
    #sq_po = pd.read_csv('123.csv')
    sq_po = pd.DataFrame(sq_po)

    #if 'prd' in sq_po.columns:
        #sq_po.drop(sq_po[sq_po['prd'] == "I"].index, inplace = True)
        #print("Cancel")
    
    sq_po = sq_po.sort_values("netqty")



    #print(sq_po)
    #sq_po.to_csv("123.csv")

    return sq_po


def fetch_orderbook():
    global ord_book
    ord_book = api.get_order_book()
    ord_po = pd.DataFrame(ord_book)
    ord_po = ord_po.loc[ord_po['status'] == "OPEN"]
    return ord_po


def cancel_order():
    ord_po = fetch_orderbook()
    for x in range(0,len(ord_po.index)):
        ret = api.cancel_order(orderno=int(ord_po.iloc[x]["norenordno"]))




    #if 'prd' in sq_po.columns:
        #sq_po.drop(sq_po[sq_po['prd'] == "I"].index, inplace = True)
        #print("Cancel")

    #ord_po.to_csv("ord.csv")
    
    #sq_po = sq_po.sort_values("netqty")



    #print(sq_po)
    #sq_po.to_csv("123.csv")

    #return sq_po

def Refresh_qtys():
    sq_po = fetch_positions()

    #print("In Refresh Qtys")
    Refresh_qtys_Main(sq_po)
    Refresh_qtys_hedges(sq_po)


def Refresh_qtys_Main(sq_po):

 #Major change 08.07.2023

    for x in range(0,len(sq_po.index)):

        for i in range(1, depth+2):
            if sq_po.iloc[x]["tsym"] == row[i]["ce_tsym"]:
                #print(row[i]["ce_tsym"],sq_po.iloc[x]["netqty"])
                ce_qty_labels[i-1]["text"] = sq_po.iloc[x]["netqty"]
                break
            

        for i in range(1, depth+2):
            if sq_po.iloc[x]["tsym"] == row_PE[i]["pe_tsym"]:
                #print(row_PE[i]["pe_tsym"],sq_po.iloc[x]["netqty"])
                pe_qty_labels[i-1]["text"] = sq_po.iloc[x]["netqty"]
                break



def Refresh_qtys_hedges(sq_po):
    for x in range(0,len(sq_po.index)):
        #print(x)
        for i in range(1, depth_hedge):
            #print(i)
            #print("Inside--->",x,i,sq_po.iloc[x]["tsym"],sq_po.iloc[x]["token"],sq_po.iloc[x]["netqty"],row_CE_hedge[i]["ce_tsym"],int(row_CE_hedge[i]["ce_token"]))
            if sq_po.iloc[x]["tsym"]== row_CE_hedge[i]["ce_tsym"]:
                #print("Success")
                row_CE_hedge[i]["ce_active_qty"] = int(sq_po.iloc[x]["netqty"])
                ce_hedge_qty_labels[i-1]['text'] = row_CE_hedge[i]["ce_active_qty"]
                #print(sq_po.iloc[x]["netqty"])
                #print(row_CE_hedge[i]["ce_active_qty"])
                break

            if sq_po.iloc[x]["tsym"]== row_PE_hedge[i]["pe_tsym"]:
                #print("Success")
                row_PE_hedge[i]["pe_active_qty"] = int(sq_po.iloc[x]["netqty"])
                pe_hedge_qty_labels[i-1]["text"] = row_PE_hedge[i]["pe_active_qty"]
                # print(sq_po.iloc[x]["netqty"])
                #print(row_PE_hedge[i]["pe_active_qty"])
                break


root.mainloop()
