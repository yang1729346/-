import streamlit as st
import pandas as pd
import datetime

# --- 1. 页面基本设置 ---
st.set_page_config(page_title="磊子的专属课表", page_icon="📅", layout="wide")

# --- 2. 课表解析逻辑 ---
def parse_week_string(week_str):
    valid_weeks = set()
    parts = week_str.split(',')
    for part in parts:
        part = part.strip()
        if not part: continue
        # 处理单双周逻辑
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

# --- 3. 核心课表数据 ---
MY_COURSES = [
    {'课程名称': '保险精算学', '教师': '岁磊', '地点': '弘文楼1104A', 'day': 1, '节次': ['第一节\n(08:00-08:45)', '第二节\n(08:55-09:40)'], 'weeks_raw': '1-3周,5-16周'},
    {'课程名称': '保险经营管理学', '教师': '轩会永', '地点': '弘文楼1203A', 'day': 1, '节次': ['第三节\n(10:00-10:45)', '第四节\n(10:55-11:40)'], 'weeks_raw': '1-16周'},
    {'课程名称': 'Python金融数据分析', '教师': '贾甜甜', '地点': '真知楼201B(机房)', 'day': 2, '节次': ['第一节\n(08:00-08:45)', '第二节\n(08:55-09:40)'], 'weeks_raw': '1-16周'},
    {'课程名称': '大学生职业发展与就业指导(二)', '教师': '李幸霞', '地点': '弘毅楼3215D', 'day': 2, '节次': ['第三节\n(10:00-10:45)', '第四节\n(10:55-11:40)'], 'weeks_raw': '1-8周'},
    {'课程名称': '再保险', '教师': '陶海鑫', '地点': '弘文楼1215D', 'day': 3, '节次': ['第八节\n(16:00-16:45)', '第九节\n(16:55-17:40)'], 'weeks_raw': '1-8周'},
    {'课程名称': '保险精算学', '教师': '岁磊', '地点': '弘文楼1201A', 'day': 4, '节次': ['第一节\n(08:00-08:45)', '第二节\n(08:55-09:40)'], 'weeks_raw': '1-3周(单),6-14周(双),15-16周'}
]

# --- 4. 界面渲染 ---
st.title("📅 磊子的专属课表")

# 计算当前时间信息
start_date = datetime.date(2026, 3, 2)
today = datetime.date.today()
current_week = ((today - start_date).days // 7) + 1
current_day = today.isoweekday()
weekday_cn = {1: '一', 2: '二', 3: '三', 4: '四', 5: '五', 6: '六', 7: '日'}

# 顶部状态栏
st.info(f"今天是：2026年3月16日 | 星期{weekday_cn.get(current_day, '休')} | 本学期第 {current_week} 周")

# 初始化表格框架
periods = [
    '第一节\n(08:00-08:45)', '第二节\n(08:55-09:40)', '第三节\n(10:00-10:45)', 
    '第四节\n(10:55-11:40)', '第五节\n(11:40-12:30)', '第六节\n(14:00-14:45)', 
    '第七节\n(14:55-15:40)', '第八节\n(16:00-16:45)', '第九节\n(16:55-17:40)', 
    '第十节\n(18:40-19:25)', '第十一节\n(19:35-20:20)', '第十二节\n(20:30-21:15)', 
    '第十三节\n(21:25-22:10)'
]
days = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
grid = {day: [""] * len(periods) for day in days}
grid['时间段'] = periods

# 填充数据
for c in MY_COURSES:
    if current_week in parse_week_string(c['weeks_raw']):
        d_name = days[c['day'] - 1]
        for p in c['节次']:
            if p in periods:
                grid[d_name][periods.index(p)] = f"{c['课程名称']}\n@{c['地点']}"

# 显示表格
df = pd.DataFrame(grid)
st.table(df[['时间段'] + days])

# 底部备注
st.caption("💡 实践课提醒：第17周 保险产品设计与规划(黄祖梅) | 第18周 保险精算实验(岁磊)")
