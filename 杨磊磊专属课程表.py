import streamlit as st
import datetime
import time

# --- 把容易导致崩溃的库放到安全区域 ---
try:
    import pandas as pd
    import requests
    ENV_OK = True
except ImportError as e:
    ENV_OK = False
    MISSING_MODULE = str(e)

st.set_page_config(page_title="自律与投资看板", page_icon="📈", layout="wide")

if not ENV_OK:
    st.error(f"🚨 环境配置错误！缺少工具包：{MISSING_MODULE}")
    st.warning("请确保你的 GitHub 仓库里有一个名为 `requirements.txt` 的文件，并且里面写了 `pandas` 和 `requests`。")
    st.stop() # 停止运行，防止出现 Oh no

# --- 股票获取逻辑 (增加极端错误隔离) ---
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
                'volume': int(raw[36])
            }
            time_str = raw[30]
            if len(time_str) >= 14:
                results[code]['time'] = f"{time_str[8:10]}:{time_str[10:12]}:{time_str[12:14]}"
            else:
                results[code]['time'] = time_str
        return results
    except Exception as e:
        return {"error": str(e)}

# --- 课表数据 ---
MY_COURSES = [
    {'课程名称': '保险精算学', '教师': '岁磊', '地点': '弘文楼1104A', 'day': 1, '节次': ['第一节\n(08:00-08:45)', '第二节\n(08:55-09:40)'], 'weeks_raw': '1-3周,5-16周'},
    {'课程名称': '保险经营管理学', '教师': '轩会永', '地点': '弘文楼1203A', 'day': 1, '节次': ['第三节\n(10:00-10:45)', '第四节\n(10:55-11:40)'], 'weeks_raw': '1-16周'},
    {'课程名称': 'Python金融数据分析', '教师': '贾甜甜', '地点': '真知楼201B(机房)', 'day': 2, '节次': ['第一节\n(08:00-08:45)', '第二节\n(08:55-09:40)'], 'weeks_raw': '1-16周'},
    {'课程名称': '大学生职业发展与就业指导(二)', '教师': '李幸霞', '地点': '弘毅楼3215D', 'day': 2, '节次': ['第三节\n(10:00-10:45)', '第四节\n(10:55-11:40)'], 'weeks_raw': '1-8周'},
    {'课程名称': '再保险', '教师': '陶海鑫', '地点': '弘文楼1215D', 'day': 3, '节次': ['第八节\n(16:00-16:45)', '第九节\n(16:55-17:40)'], 'weeks_raw': '1-8周'},
    {'课程名称': '保险精算学', '教师': '岁磊', '地点': '弘文楼1201A', 'day': 4, '节次': ['第一节\n(08:00-08:45)', '第二节\n(08:55-09:40)'], 'weeks_raw': '1-3周(单),6-14周(双),15-16周'}
]

# --- 界面布局 ---
col1, col2 = st.columns([3, 1])
with col1:
    st.title("📈 实时盯盘看板")
with col2:
    st.write("")
    auto_refresh = st.toggle("开启5秒刷新", value=False)

# 渲染股票
stocks = get_multi_stock_data()
if stocks and "error" not in stocks:
    for code in ["000630", "600783"]:
        s = stocks.get(code)
        if not s: continue
        pct = 0 if s['last_close'] == 0 else ((s['price'] - s['last_close']) / s['last_close']) * 100
        
        st.subheader(f"{s['name']} ({code})")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("当前价", f"{s['price']:.2f}", f"{pct:+.2f}%")
        c2.metric("最高", f"{s['high']:.2f}")
        c3.metric("最低", f"{s['low']:.2f}")
        c4.metric("成交量", f"{s['volume']:,.0f} 手")
    
    # 安全获取时间
    try:
        first_stock_time = list(stocks.values())[0]['time']
        st.caption(f"接口更新时间：{first_stock_time} | 网页后台：{datetime.datetime.now().strftime('%H:%M:%S')}")
    except:
        pass
elif stocks and "error" in stocks:
    st.warning(f"行情接口请求失败，但不影响课表显示。错误信息: {stocks['error']}")
else:
    st.warning("暂无行情数据，可能处于非交易时间。")

st.divider()

# --- 渲染课表 (不管股票成不成功，课表必须出来) ---
st.header("📅 本周专属课表")
start_date = datetime.date(2026, 3, 2)
today = datetime.date.today()
current_week = ((today - start_date).days // 7) + 1
current_day = today.isoweekday()
weekday_cn = {1: '一', 2: '二', 3: '三', 4: '四', 5: '五', 6: '六', 7: '日'}

st.info(f"第 {current_week} 周 | 星期{weekday_cn.get(current_day, '休')}")

periods = ['第一节\n(08:00-08:45)', '第二节\n(08:55-09:40)', '第三节\n(10:00-10:45)', '第四节\n(10:55-11:40)', '第五节\n(11:40-12:30)', '第六节\n(14:00-14:45)', '第七节\n(14:55-15:40)', '第八节\n(16:00-16:45)', '第九节\n(16:55-17:40)', '第十节\n(18:40-19:25)', '第十一节\n(19:35-20:20)', '第十二节\n(20:30-21:15)', '第十三节\n(21:25-22:10)']
days = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
grid = {day: [""] * len(periods) for day in days}
grid['时间'] = periods

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

for c in MY_COURSES:
    if current_week in parse_week_string(c['weeks_raw']):
        d_name = days[c['day'] - 1]
        for p in c['节次']:
            if p in periods:
                grid[d_name][periods.index(p)] = f"{c['课程名称']}\n@{c['地点']}"

st.table(pd.DataFrame(grid)[['时间'] + days])

if auto_refresh:
    time.sleep(5)
    st.rerun()
