import streamlit as st
import pandas as pd
import datetime
import requests
import time

# --- 1. 页面基本设置 ---
st.set_page_config(page_title="自律与投资看板", page_icon="📈", layout="wide")

# --- 2. 腾讯行情接口 (更稳定，防云端拦截) ---
def get_multi_stock_data():
    url = "http://qt.gtimg.cn/q=sz000630,sh600783"
    try:
        response = requests.get(url, timeout=3)
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
                'volume': int(raw[36]) # 腾讯接口直接返回“手”
            }
            # 格式化时间 (例如把 20260305150000 变成 15:00:00)
            time_str = raw[30]
            if len(time_str) >= 14:
                results[code]['time'] = f"{time_str[8:10]}:{time_str[10:12]}:{time_str[12:14]}"
            else:
                results[code]['time'] = time_str
                
        return results
    except Exception as e:
        return None

# --- 3. 课表解析逻辑 ---
def parse_week_string(week_str):
    valid_weeks = set()
    parts = week_str.split(',')
    for part in parts:
        part = part.strip()
        if not part: continue
        is_odd = '(单)' in part
        is_even = '(双)' in part
        part = part.replace('(单)', '').replace('(双)', '').replace('周', '').strip()
        if '-' in part:
            start, end = map(int, part.split('-'))
            for w in range(start, end + 1):
                if is_odd and w % 2 == 0: continue
                if is_even and w % 2 != 0: continue
                valid_weeks.add(w)
        elif part.isdigit():
            w = int(part)
            if is_odd and w % 2 == 0: continue
            if is_even and w % 2 != 0: continue
            valid_weeks.add(w)
    return valid_weeks

MY_COURSES = [
    {'课程名称': '保险精算学', '教师': '岁磊', '地点': '弘文楼1104A', 'day': 1, '节次': ['第一节\n(08:00-08:45)', '第二节\n(08:55-09:40)'], 'weeks_raw': '1-3周,5-16周'},
    {'课程名称': '保险经营管理学', '教师': '轩会永', '地点': '弘文楼1203A', 'day': 1, '节次': ['第三节\n(10:00-10:45)', '第四节\n(10:55-11:40)'], 'weeks_raw': '1-16周'},
    {'课程名称': 'Python金融数据分析', '教师': '贾甜甜', '地点': '真知楼201B(机房)', 'day': 2, '节次': ['第一节\n(08:00-08:45)', '第二节\n(08:55-09:40)'], 'weeks_raw': '1-16周'},
    {'课程名称': '大学生职业发展与就业指导(二)', '教师': '李幸霞', '地点': '弘毅楼3215D', 'day': 2, '节次': ['第三节\n(10:00-10:45)', '第四节\n(10:55-11:40)'], 'weeks_raw': '1-8周'},
    {'课程名称': '再保险', '教师': '陶海鑫', '地点': '弘文楼1215D', 'day': 3, '节次': ['第八节\n(16:00-16:45)', '第九节\n(16:55-17:40)'], 'weeks_raw': '1-8周'},
    {'课程名称': '保险精算学', '教师': '岁磊', '地点': '弘文楼1201A', 'day': 4, '节次': ['第一节\n(08:00-08:45)', '第二节\n(08:55-09:40)'], 'weeks_raw': '1-3周(单),6-14周(双),15-16周'}
]

# --- 4. 界面渲染 ---
col_title, col_toggle = st.columns([3, 1])
with col_title:
    st.title("📈 实时盯盘")
with col_toggle:
    st.write("") # 占位对齐
    # 这里就是防止崩溃的核心：默认关闭刷新，由你手动控制
    auto_refresh = st.toggle("开启 5 秒自动刷新", value=False)

stocks = get_multi_stock_data()

if stocks:
    for code in ["000630", "600783"]:
        s = stocks.get(code)
        if not s: continue
        
        # 预防刚开盘或停牌导致的错误
        if s['last_close'] == 0:
            pct = 0
        else:
            pct = ((s['price'] - s['last_close']) / s['last_close']) * 100
            
        st.subheader(f"{s['name']} ({code})")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("当前价", f"{s['price']:.2f}", f"{pct:+.2f}%")
        c2.metric("最高", f"{s['high']:.2f}")
        c3.metric("最低", f"{s['low']:.2f}")
        c4.metric("成交量", f"{s['volume']:,.0f} 手")
    
    st.caption(f"数据获取时间：{list(stocks.values())[0]['time']} (网页更新于: {datetime.datetime.now().strftime('%H:%M:%S')})")
else:
    st.warning("⚠️ 暂时无法获取股票数据，可能非交易时段或接口正在维护。")

st.divider()

# --- 5. 课表绘制 ---
st.header("📅 本周课表预览")
start_date = datetime.date(2026, 3, 2)
today = datetime.date.today()
current_week = ((today - start_date).days // 7) + 1
current_day = today.isoweekday()
weekday_cn = {1: '一', 2: '二', 3: '三', 4: '四', 5: '五', 6: '六', 7: '日'}

st.info(f"今天是星期{weekday_cn.get(current_day, '休')}，本学期第 {current_week} 周")

periods = ['第一节\n(08:00-08:45)', '第二节\n(08:55-09:40)', '第三节\n(10:00-10:45)', '第四节\n(10:55-11:40)', '第五节\n(11:40-12:30)', '第六节\n(14:00-14:45)', '第七节\n(14:55-15:40)', '第八节\n(16:00-16:45)', '第九节\n(16:55-17:40)', '第十节\n(18:40-19:25)', '第十一节\n(19:35-20:20)', '第十二节\n(20:30-21:15)', '第十三节\n(21:25-22:10)']
days = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
grid = {day: [""] * len(periods) for day in days}
grid['时间'] = periods

for c in MY_COURSES:
    if current_week in parse_week_string(c['weeks_raw']):
        d_name = days[c['day'] - 1]
        for p in c['节次']:
            if p in periods:
                grid[d_name][periods.index(p)] = f"{c['课程名称']}\n@{c['地点']}"

st.table(pd.DataFrame(grid)[['时间'] + days])

# --- 6. 5秒自动刷新核心逻辑 ---
if auto_refresh:
    time.sleep(5)
    st.rerun()
