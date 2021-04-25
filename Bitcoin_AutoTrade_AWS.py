import time
import pyupbit
import datetime
from slacker import Slacker

access = ""          # 본인 값으로 변경
secret = ""          # 본인 값으로 변경

def send_log_to_slack(user_name, msg):
    ts = datetime.datetime.now().strftime('%H:%M:%S')
    msg = '%s %s'%(ts, msg)
    token = ''
    slack = Slacker(token)
    slack.chat.post_message('#coinbot', msg, username=user_name)

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("Autotrade started")
send_log_to_slack('Home Desktop', 'Autotrade started')

# 자동매매 시작
time_delay = 30 # 기본 오전 9시로부터 지연시간(분) 설정
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC") + datetime.timedelta(minutes=time_delay)
        end_time = start_time + datetime.timedelta(days=1)

        if start_time < now < end_time - datetime.timedelta(seconds=10):
            target_price = get_target_price("KRW-BTC", 0.5)
            current_price = get_current_price("KRW-BTC")
            if target_price <= current_price:
                krw = get_balance("KRW")
                if krw > 5000:
                    upbit.buy_market_order("KRW-BTC", krw*0.9995)
                    send_log_to_slack('Home Desktop', '매수완료. 매수가 : ', str(current_price), ' / 목표가 :', str(target_price))
        else:
            btc = get_balance("BTC")
            current_price = get_current_price("KRW-BTC")
            btc_balance_as_krw = btc * current_price
            if btc_balance_as_krw > 5000:
                upbit.sell_market_order("KRW-BTC", btc*0.9995)
                send_log_to_slack('Home Desktop', '매도완료. 매도가 : ', str(current_price))
        time.sleep(60)
    except Exception as e:
        print(e)
        time.sleep(60)