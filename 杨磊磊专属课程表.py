import streamlit as st
import pandas as pd
import datetime
import requests

# --- 1. 页面基本设置 ---
st.set_page_config(page_title="磊子的自律看板", page_icon="📈", layout="wide")

# --- 2. 课表解析逻辑 (保持静态) ---
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

# --- 3. 课表展示 (置顶) ---
st.header("📅 磊子的专属课表")
start_date = datetime.date(2026, 3, 2)
today = datetime.date.today()
current_week = ((today - start_date).days // 7) + 1
current_day = today.isoweekday()
weekday_cn = {1: '一', 2: '二', 3: '三', 4: '四', 5: '五', 6: '六', 7: '日'}

st.info(f"第 {current_week} 周 | 星期{weekday_cn.get(current_day, '休')}")

periods = ['第一节\n(08:00-08:45)', '第二节\n(08:55-09:40)', '第三节\n(10:00-10:45)', '第四节\n(10:55-11:40)', '第五节\n(11:40-12:30)', '第六节\n(14:00-14:45)', '第七节\n(14:55-15:40)', '第八节\n(16:00-16:45)', '第九节\n(16:55-17:40)', '第十节\n(18:40-19:25)', '第十一节\n(19:35-20:20)', '第十二节\n(20:30-21:15)', '第十三节\n(21:25-22:10)']
days = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
grid = {day: [""] * len(periods) for day in days}
grid['时间段'] = periods

for c in MY_COURSES:
    if current_week in parse_week_string(c['weeks_raw']):
        d_name = days[c['day'] - 1]
        for p in c['节次']:
            if p in periods:
                grid[d_name][periods.index(p)] = f"{c['课程名称']}\n@{c['地点']}"

st.table(pd.DataFrame(grid)[['时间段'] + days])
st.caption("💡 实践课：第17周 保险产品设计与规划 | 第18周 保险精算实验")

st.divider()

# --- 4. 铜陵有色行情抓取 ---
def get_stock_data():
    url = "http://qt.gtimg.cn/q=sz000630"
    try:
        response = requests.get(url, timeout=2)
        response.encoding = 'gbk'
        raw = response.text.split('"')[1].split('~')
        return {
            'name': raw[1], 'price': float(raw[3]), 'last_close': float(raw[4]),
            'high': float(raw[33]), 'low': float(raw[34]), 'volume': int(raw[36]),
            'time': f"{raw[30][8:10]}:{raw[30][10:12]}:{raw[30][12:14]}"
        }
    except:
        return None

# --- 5. 底部：仿同花顺盯盘区域 ---
st.header("📈 铜陵有色 (000630) 实时盯盘")

@st.fragment(run_every=3)
def render_stock_module():
    s = get_stock_data()
    if s:
        pct = ((s['price'] - s['last_close']) / s['last_close']) * 100
        
        # 顶部指标栏
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("当前价", f"{s['price']:.2f}", f"{pct:+.2f}%")
        c2.metric("最高", f"{s['high']:.2f}")
        c3.metric("最低", f"{s['low']:.2f}")
        c4.metric("成交", f"{s['volume']:,.0f} 手")

        # --- 仿同花顺多周期 K 线切换 ---
        st.write("### 行情走势")
        # 创建四个标签页
        tab1, tab2, tab3, tab4 = st.tabs(["分时图", "日K线", "周K线", "月K线"])
        
        # 为了防止图片缓存，加入当前时间戳
        ts = datetime.datetime.now().timestamp()
        
        with tab1:
            st.image(f"http://image.sinajs.cn/newchart/min/n/sz000630.gif?t={ts}", use_container_width=True)
        with tab2:
            st.image(f"http://image.sinajs.cn/newchart/daily/n/sz000630.gif?t={ts}", use_container_width=True)
        with tab3:
            st.image(f"http://image.sinajs.cn/newchart/weekly/n/sz000630.gif?t={ts}", use_container_width=True)
        with tab4:
            st.image(f"http://image.sinajs.cn/newchart/monthly/n/sz000630.gif?t={ts}", use_container_width=True)
            
        st.caption(f"最后刷新：{datetime.datetime.now().strftime('%H:%M:%S')} | 数据来源：腾讯/新浪财经")
    else:
        st.warning("行情连接中...")

render_stock_module()
