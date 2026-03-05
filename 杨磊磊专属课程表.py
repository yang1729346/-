import streamlit as st
import pandas as pd
import datetime

# --- 页面基本设置 ---
st.set_page_config(page_title="杨磊磊的专属课表", page_icon="📅", layout="wide")


# --- 核心解析逻辑 ---
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


# --- 你的个人专属课表数据（直接内置，永不丢失！） ---
MY_COURSES = [
    {
        '课程名称': '保险精算学',
        '教师': '岁磊',
        '地点': '弘文楼1104A',
        'day': 1,  # 星期一
        '节次': ['第一节\n(08:00-08:45)', '第二节\n(08:55-09:40)'],
        'weeks_raw': '1-3周,5-16周'
    },
    {
        '课程名称': '保险经营管理学',
        '教师': '轩会永',
        '地点': '弘文楼1203A',
        'day': 1,  # 星期一
        '节次': ['第三节\n(10:00-10:45)', '第四节\n(10:55-11:40)'],
        'weeks_raw': '1-16周'
    },
    {
        '课程名称': 'Python金融数据分析',
        '教师': '贾甜甜',
        '地点': '真知楼201B(机房)',
        'day': 2,  # 星期二
        '节次': ['第一节\n(08:00-08:45)', '第二节\n(08:55-09:40)'],
        'weeks_raw': '1-16周'
    },
    {
        '课程名称': '大学生职业发展与就业指导(二)',
        '教师': '李幸霞',
        '地点': '弘毅楼3215D',
        'day': 2,  # 星期二
        '节次': ['第三节\n(10:00-10:45)', '第四节\n(10:55-11:40)'],
        'weeks_raw': '1-8周'
    },
    {
        '课程名称': '再保险',
        '教师': '陶海鑫',
        '地点': '弘文楼1215D',
        'day': 3,  # 星期三
        '节次': ['第八节\n(16:00-16:45)', '第九节\n(16:55-17:40)'],
        'weeks_raw': '1-8周'
    },
    {
        '课程名称': '保险精算学',
        '教师': '岁磊',
        '地点': '弘文楼1201A',
        'day': 4,  # 星期四
        '节次': ['第一节\n(08:00-08:45)', '第二节\n(08:55-09:40)'],
        'weeks_raw': '1-3周(单),6-14周(双),15-16周'
    }
]

# --- 网页界面显示 ---
st.title("🎓 杨磊磊的专属课表")

# 获取时间和数据
start_date = datetime.date(2026, 3, 2)
today = datetime.date.today()
delta = today - start_date
current_week = (delta.days // 7) + 1
current_day = today.isoweekday()

weekday_cn = {1: '一', 2: '二', 3: '三', 4: '四', 5: '五', 6: '六', 7: '日'}

st.info(
    f"**查阅日期**：{today.strftime('%Y年%m月%d日')} (星期{weekday_cn[current_day]})  |  **当前进度**：本学期 第 {current_week} 周")

st.subheader(f"📅 第 {current_week} 周 完整排课")

# 1. 准备大表格表头（完整时间段）
periods = [
    '第一节\n(08:00-08:45)', '第二节\n(08:55-09:40)', '第三节\n(10:00-10:45)', '第四节\n(10:55-11:40)',
    '第五节\n(11:40-12:30)', '第六节\n(14:00-14:45)', '第七节\n(14:55-15:40)', '第八节\n(16:00-16:45)',
    '第九节\n(16:55-17:40)', '第十节\n(18:40-19:25)', '第十一节\n(19:35-20:20)', '第十二节\n(20:30-21:15)',
    '第十三节\n(21:25-22:10)'
]
days = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']

# 初始化空网格
schedule_grid = {day: [""] * len(periods) for day in days}
schedule_grid['上课时间'] = periods

# 2. 将本周有课的内容填入对应的时间格子里
for c in MY_COURSES:
    weeks = parse_week_string(c['weeks_raw'])
    if current_week in weeks:
        day_name = days[c['day'] - 1]
        for period_name in c['节次']:
            if period_name in periods:
                p_idx = periods.index(period_name)
                cell_text = f"📚{c['课程名称']}\n📍{c['地点']}\n👨‍🏫{c['教师']}"
                schedule_grid[day_name][p_idx] = cell_text

# 3. 生成表格格式并调整列的顺序
df = pd.DataFrame(schedule_grid)
df = df[['上课时间', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']]

# 4. 在网页上画出这个大表格
st.table(df)

# 5. 底部贴心提示实践课
st.markdown("---")
st.markdown("💡 **温馨提示（期末实践课程安排）**：")
st.markdown("- **保险产品设计与保险规划** (黄祖梅)：第 17 周")
st.markdown("- **保险精算实验** (岁磊)：第 18 周")
