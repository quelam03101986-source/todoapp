import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import date, datetime

# --- 1. DATABASE FUNCTIONS---
DB = "todo.db"

def init_db():
    with sqlite3.connect(DB) as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS tasks 
            (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, status TEXT, date TEXT, user TEXT, note TEXT)""")

def add_tk(name, stat, dt, user, note):
    with sqlite3.connect(DB) as conn:
        conn.execute("INSERT INTO tasks (name, status, date, user, note) VALUES (?,?,?,?,?)", (name, stat, str(dt), user, note))

def get_tk():
    with sqlite3.connect(DB) as conn:
        return pd.read_sql("SELECT * FROM tasks", conn)

def get_tk_id(tid):
    with sqlite3.connect(DB) as conn:
        return conn.execute("SELECT * FROM tasks WHERE id=?", (tid,)).fetchone()

def upd_tk(tid, name, stat, dt, user, note):
    with sqlite3.connect(DB) as conn:
        conn.execute("UPDATE tasks SET name=?, status=?, date=?, user=?, note=? WHERE id=?", (name, stat, str(dt), user, note, tid))

def del_tk(tid):
    with sqlite3.connect(DB) as conn:
        conn.execute("DELETE FROM tasks WHERE id=?", (tid,))

# --- 2. GIAO DIỆN CHÍNH ---
st.set_page_config(page_title="Pro To-Do App", layout="wide")
init_db()

st.markdown("<h1 style='text-align: center; color: #4CAF50;'>📝 QUẢN LÝ CÔNG VIỆC PRO</h1>", unsafe_allow_html=True)
st.divider()

menu = ["📊 Thống kê", "📋 Quản lý", "➕ Thêm mới"]
choice = st.sidebar.selectbox("Menu", menu)

# --- CHỨC NĂNG: THÊM MỚI ---
if choice == "➕ Thêm mới":
    st.subheader("Tạo công việc mới")
    with st.form("add_f"):
        c1, c2 = st.columns(2)
        name = c1.text_input("Tên việc (*)")
        user = c1.text_input("Người phụ trách")
        dt = c2.date_input("Hạn chót", date.today())
        stat = c2.selectbox("Trạng thái", ["Chưa bắt đầu", "Đang làm", "Hoàn thành"])
        note = st.text_area("Ghi chú")
        if st.form_submit_button("Lưu"):
            if name:
                add_tk(name, stat, dt, user, note)
                st.success("Đã thêm!")
            else: st.error("Thiếu tên việc!")

# --- CHỨC NĂNG: QUẢN LÝ (VIEW, FILTER, EDIT, DELETE) ---
elif choice == "📋 Quản lý":
    df = get_tk()
    col_f1, col_f2 = st.columns(2)
    search = col_f1.text_input("🔍 Tìm tên việc")
    f_stat = col_f2.selectbox("Lọc trạng thái", ["Tất cả"] + ["Chưa bắt đầu", "Đang làm", "Hoàn thành"])

    if search: df = df[df['name'].str.contains(search, case=False)]
    if f_stat != "Tất cả": df = df[df['status'] == f_stat]

    st.dataframe(df, use_container_width=True)
    st.download_button("📥 Tải CSV", df.to_csv(index=False).encode('utf-8-sig'), "tasks.csv", "text/csv")

    st.divider()
    st.subheader("🛠 Thao tác công việc")
    if not df.empty:
        tid = st.selectbox("Chọn ID", df['id'].tolist())
        t_data = get_tk_id(tid)
        t_edit, t_del = st.tabs(["✏️ Sửa", "🗑️ Xóa"])

        with t_edit:
            with st.form("edit_f"):
                n_name = st.text_input("Tên việc", t_data[1])
                n_user = st.text_input("Phụ trách", t_data[4])
                # Ép kiểu date an toàn
                try: d_val = datetime.strptime(t_data[3], '%Y-%m-%d').date()
                except: d_val = date.today()
                n_dt = st.date_input("Hạn", d_val)
                n_stat = st.selectbox("Trạng thái", ["Chưa bắt đầu", "Đang làm", "Hoàn thành"], 
                                      index=["Chưa bắt đầu", "Đang làm", "Hoàn thành"].index(t_data[2]))
                n_note = st.text_area("Ghi chú", t_data[5])
                if st.form_submit_button("Cập nhật"):
                    upd_tk(tid, n_name, n_stat, n_dt, n_user, n_note)
                    st.rerun()

        with t_del:
            if st.button("Xác nhận Xóa"):
                del_tk(tid)
                st.rerun()

# --- CHỨC NĂNG: THỐNG KÊ (DASHBOARD) ---
else:
    st.subheader("📊 Tổng quan tiến độ")
    df = get_tk()
    if not df.empty:
        m1, m2, m3 = st.columns(3)
        m1.metric("Tổng việc", len(df))
        m2.metric("Hoàn thành", len(df[df['status'] == 'Hoàn thành']))
        m3.metric("Đang làm", len(df[df['status'] == 'Đang làm']))

        c1, c2 = st.columns(2)
        with c1:
            fig1 = px.pie(df, names='status', title="Tỷ lệ trạng thái", hole=0.4)
            st.plotly_chart(fig1, use_container_width=True)
        with c2:
            fig2 = px.bar(df['user'].value_counts().reset_index(), x='user', y='count', title="Việc theo nhân sự")
            st.plotly_chart(fig2, use_container_width=True)
    else: st.info("Chưa có dữ liệu.")

st.sidebar.write("🔥 GV: ia minh")
