import time
import pyupbit
import datetime
from slacker import Slacker

access = ""          # 본인 값으로 변경!
secret = ""          # 본인 값으로 변경!

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

# 자동매매 시작, !모든 암호화폐를 원화로 매도하여 준비되었는지 확인!
time_delay = 30 # 기본 오전 9시로부터 지연시간(분) 설정
krw = get_balance("KRW")
if krw is None: krw = 0
alive_alarm = 0
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC") + datetime.timedelta(minutes=time_delay)
        end_time = start_time + datetime.timedelta(days=1)

        if start_time < now < end_time - datetime.timedelta(minutes=5):
            # KRW-BTC
            target_price_BTC = get_target_price("KRW-BTC", 0.5)
            current_price_BTC = get_current_price("KRW-BTC")
            btc = get_balance("BTC")
            if btc is None: btc = 0

            # KRW-ETH
            target_price_ETH = get_target_price("KRW-ETH", 0.5)
            current_price_ETH = get_current_price("KRW-ETH")
            eth = get_balance("ETH")
            if eth is None: eth = 0

            if (target_price_BTC <= current_price_BTC) and (btc == 0):
                if eth == 0:
                    buykrw = krw / 2
                else:
                    buykrw = get_balance("KRW")

                if buykrw > 5000:
                    upbit.buy_market_order("KRW-BTC", buykrw * 0.9995)
                    send_log_to_slack('Home Desktop', f'[KRW-BTC] 매수완료. 매수가 : {target_price_BTC:,.0f} / 목표가 : {current_price_BTC:,.0f}')
                else:
                    send_log_to_slack('Home Desktop', f'[KRW-BTC] 원화 잔고 부족')

            if (target_price_ETH <= current_price_ETH) and (eth == 0):
                if btc == 0:
                    buykrw = krw / 2
                else:
                    buykrw = get_balance("KRW")

                if buykrw > 5000:
                    upbit.buy_market_order("KRW-ETH", buykrw * 0.9995)
                    send_log_to_slack('Home Desktop', f'[KRW-ETH] 매수완료. 매수가 : {target_price_ETH:,.0f} / 목표가 : {current_price_ETH:,.0f}')
                else:
                    send_log_to_slack('Home Desktop', f'[KRW-ETH] 원화 잔고 부족')

        else:
            btc = get_balance("BTC")
            if btc is None: btc = 0
            current_price_BTC = get_current_price("KRW-BTC")
            btc_balance_as_krw = btc * current_price_BTC

            eth = get_balance("ETH")
            if eth is None: eth = 0
            current_price_ETH = get_current_price("KRW-ETH")
            eth_balance_as_krw = eth * current_price_ETH

            if btc_balance_as_krw > 5000:
                upbit.sell_market_order("KRW-BTC", btc)
                send_log_to_slack('Home Desktop', f'[KRW-BTC] 매도완료. 매도가 : {current_price_BTC:,.0f}')
            elif btc_balance_as_krw > 0:
                send_log_to_slack('Home Desktop', '[KRW-BTC] 매도잔고 부족')

            if eth_balance_as_krw > 5000:
                upbit.sell_market_order("KRW-ETH", eth)
                send_log_to_slack('Home Desktop', f'[KRW-ETH] 매도완료. 매도가 : {current_price_ETH:,.0f}')
            elif eth_balance_as_krw > 0:
                send_log_to_slack('Home Desktop', '[KRW-ETH] 매도잔고 부족')

            krw = get_balance("KRW")
            if krw is None: krw = 0

        if alive_alarm == 360:
            alive_alarm = 0
            send_log_to_slack('Home Desktop', f'코인봇 정상작동 중 : {now}')
        else:
            alive_alarm = alive_alarm + 1

        time.sleep(10)

    except Exception as e:
        print(e)
        time.sleep(10)