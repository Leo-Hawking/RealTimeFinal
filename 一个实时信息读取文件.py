import nest_asyncio
nest_asyncio.apply()
# 2. 初始化客户端
# trading_client 负责下单 (受 200次/分 限制)

from alpaca.data.live import StockDataStream
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
import threading

# 1. 配置
SYMBOL = "SPY"
API_KEY = "PKSDAPKWYHCIMZSECNF2GH74PT"      # 替换为你的 Key (以 PK 开头)
SECRET_KEY = "DVNTCYQYmcZ2fTHFyqiSFSQyKEtPfTpzSH2cTfX1Cwqq" # 替换为你的 Secret

# 2. 初始化客户端
# trading_client 负责下单 (受 200次/分 限制)
trading_client = TradingClient(API_KEY, SECRET_KEY, paper=True)
# data_stream 负责接收数据 (不受 REST 限制，无限接收)
data_stream = StockDataStream(API_KEY, SECRET_KEY)

# 3. 定义策略逻辑 (这是回调函数，只有数据来了才会触发)
async def on_quote_update(quote):
    """
    当 SPY 有新的报价(L1)时，这个函数会被自动调用。
    quote.bid_price = 买一价
    quote.ask_price = 卖一价
    """
    print(f"收到报价: Bid {quote.bid_price} | Ask {quote.ask_price}")
    
    # --- 核心风控：限流 ---
    # 在这里判断：虽然数据每秒来几百次，但我不能每秒都下单。
    # 比如：只有当 (卖一价 - 买一价) > 0.03 (有利可图) 时才触发下单逻辑
    
    spread = quote.ask_price - quote.bid_price
    if spread > 0.05: # 假设我们只做大价差
        print(">>> 发现机会，尝试下单...")
        # 注意：这里下单是同步调用，可能会阻塞 WebSocket，实战中最好丢给另一个线程处理
        try:
            # 构造订单 (仅作演示，未做状态管理)
            # limit_order_data = LimitOrderRequest(...)
            # trading_client.submit_order(order_data=limit_order_data)
            pass
        except Exception as e:
            print(f"下单失败 (可能触发限流): {e}")

# 4. 启动 WebSocket
def start_bot():
    print(f"正在连接 {SYMBOL} 的实时数据流...")
    
    # 订阅报价 (Quotes) - 也就是 L1 数据
    data_stream.subscribe_quotes(on_quote_update, SYMBOL)
    
    # 开始运行 (这会阻塞主线程)
    data_stream.run()

if __name__ == "__main__":
    start_bot()
