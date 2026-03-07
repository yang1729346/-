import streamlit as st
import pandas as pd
import datetime
import requests

# --- 1. 页面基本设置 ---
st.set_page_config(page_title="自律与投资看板", page_icon="📈", layout="wide")

# --- 2. 腾讯行情接口 ---
def get_multi_stock_data():
    url = "http://qt.gtimg.cn/q=sz000630,sh600783"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=3)
        response.encoding = 'gbk'
        lines = response.text.strip().split('\n')
        results = {}
        for line in lines:
            if len(line) < 10: continue
            code = "000630" if "sz000630" in line else "600783"
            raw = line.split('"')[1].split('~')
            if len(raw) < 40: continue
            
            results[code] = {
                'name': raw[1],
                'price': float(raw[3]),
                'last_close': float(raw[4]),
                'high': float(raw[33]),
                'low': float(raw[34]),
                'volume': int(raw[36]),
                'time': f"{raw[30][8:10]}:{raw[30][10:12]}:{raw[30][12:14]}" if len(raw[30])>=14 else raw[30]
            }
        return results
    except:
        return None

# --- 3. 股票盯盘 (局部 5 秒刷新) ---
st.header("📈 实时盯盘 (5秒自动刷新)")

@st.fragment(run_every=5)
def render_stocks():
    stocks = get_multi_stock_data()
    if stocks:
        # 定义 K 线图的前缀 (新浪接口)
        # min 表示分时图，daily 表示日K线
        k_line_url_template = "http://image.sinajs.cn/newchart/min/n/{}.gif"
        
        for code in ["000630", "600783"]:
            s = stocks.get(code)
            if not s: continue
            
            full_code = f"sz{code}" if code == "000630" else f"sh{code}"
            pct = 0 if s['last_close'] == 0 else ((s['price'] - s['last_close']) / s['last_close']) * 100
            
            # --- 股票基础信息 ---
            st.subheader(f"{s['name']} ({code})")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("当前价", f"{s['price']:.2f}", f"{pct:+.2f}%")
            c2.metric("最高", f"{s['high']:.2f}")
            c3.metric("最低", f"{s['low']:.2f}")
            c4.metric("成交总量", f"{s['volume']:,.0f} 手")
            
            # --- 实时 K 线分时图 ---
            with st.expander(f"📉 点击查看 {s['name']} 实时分时图", expanded=True):
                # 后面带上时间戳防止图片缓存不更新
                img_url = k_line_url_template.format(full_code) + f"?t={datetime.datetime.now().timestamp()}"
                st.image(img_url, use_container_width=True)
            
        st.caption(f"行情时间：{list(stocks.values())[0]['time']} | 刷新于：{datetime.datetime.now().strftime('%H:%M:%S')}")
    else:
        st.warning("⚠️ 正在尝试连接行情接口...")

render_stocks()

st.divider()

# --- 4. 课表绘制 (保持静态) ---
st.header("📅 本周课表预览")
# (此处省略之前 MY_COURSES 数据和解析函数以节省篇幅，请保持你原有代码中的数据不变)
# ... [保留你原有的 MY_COURSES 和 parse_week_string 函数] ...

# 简单演示课表渲染
start_date = datetime.date(2026, 3, 2)
today = datetime.date.today()
current_week = ((today - start_date).days // 7) + 1
current_day = today.isoweekday()
weekday_cn = {1: '一', 2: '二', 3: '三', 4: '四', 5: '五', 6: '六', 7: '日'}
st.info(f"第 {current_week} 周 | 星期{weekday_cn.get(current_day, '休')}")

# [保留你原有的 grid 渲染和 st.table(df) 代码]
