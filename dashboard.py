import pandas as pd  # pip install pandas
import plotly.express as px  # pip install plotly-express
import streamlit as st  # pip install streamlit
import requests

# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title="2019 Check-ins Dashboard", page_icon=":bar_chart:", layout="wide")

options_response = requests.get("https://tm-exam-354703.uc.r.appspot.com/options").json()[0]
options_response['months_options'] = list(range(1,13))

# ---- SIDEBAR ----

st.sidebar.header("Please Filter Here:")

managers_container = st.sidebar.container()
all_managers = st.sidebar.checkbox("Select all managers")

if all_managers:
    manager = managers_container.multiselect(
        "Select Manager/s:",
        options = options_response['manager_id_options'],
        default = options_response['manager_id_options']
    )
else:
    manager =  managers_container.multiselect(
        "Select Manager/s:",
        options = options_response['manager_id_options'],
        default = options_response['manager_id_options'][:1]
    )

users_container = st.sidebar.container()
all_users = st.sidebar.checkbox("Select all users")

if all_users:
    user = users_container.multiselect(
        "Select User/s:",
        options = options_response['user_id_options'],
        default = options_response['user_id_options']
    )
else:
    user = users_container.multiselect(
        "Select User/s:",
        options = options_response['user_id_options'],
        default = options_response['user_id_options'][:1]
    )

months_container = st.sidebar.container()
all_months = st.sidebar.checkbox("Select all months")

if all_months:
    month = months_container.multiselect(
        "Select Month/s:",
        options = options_response['months_options'],
        default = options_response['months_options']
    )
else:
    month =  months_container.multiselect(
        "Select Month:",
        options = options_response['months_options'],
        default = [9]
    )

if user == [] or manager == [] or month == []:
    df_selection = pd.DataFrame()

else:
    fields = [f"user_id={','.join(str(x) for x in user)}" if not all_users else "",
            f"manager_id={','.join(str(x) for x in manager)}" if not all_managers else "",
            f"month={','.join(str(x) for x in month)}" if not all_months else ""]

    field_params = '&'.join(filter(None, fields))
    response = requests.get(f"https://tm-exam-354703.uc.r.appspot.com/?{field_params}")

    df_selection = pd.read_json(response.text)

if not df_selection.empty:
    df_selection['month'] = df_selection.date.dt.month

# ---- MAINPAGE ----
st.title(":bar_chart: 2019 Check-ins Dashboard")
st.markdown("##")

# TOP KPI's
if df_selection.empty:
    total_managers = total_users = total_months = total_hours = total_projects = 0

else:
    total_managers = len(df_selection['manager_id'].unique())
    total_users = len(df_selection['user_id'].unique())
    total_months = len(df_selection['month'].unique())
    total_hours = int(df_selection['hours'].sum())
    total_projects = len(df_selection['project_id'].unique())

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.caption("Total Managers:")
    st.subheader(f"{total_managers}")
with col2:
    st.caption("Total Users:")
    st.subheader(f"{total_users}")
with col3:
    st.caption("Total Months:")
    st.subheader(f"{total_months}")
with col4:
    st.caption("Total Hours:")
    st.subheader(f"{total_hours}")
with col5:
    st.caption("Total Projects:")
    st.subheader(f"{total_projects}")

st.markdown("""---""")

if not df_selection.empty:
    # Total hours per user [BAR CHART]
    total_hours_per_user = df_selection.groupby(by=["user_id"]).sum()[["hours"]]
    fig_user_hours = px.bar(
        total_hours_per_user,
        x=total_hours_per_user.index,
        y="hours",
        title="<b>Total hours per user</b>",
        color_discrete_sequence=["#0083B8"] * len(total_hours_per_user),
        template="plotly_white"
    )
    fig_user_hours.update_layout(
        xaxis=dict(tickmode="array", tickvals=total_hours_per_user.index),
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=(dict(showgrid=False))
    )

    # Total checkins per user [BAR CHART]
    total_checkins_per_user = df_selection.groupby(by=["user_id"]).size()
    fig_user_checkins = px.bar(
        total_checkins_per_user,
        x=total_checkins_per_user.index,
        y=total_checkins_per_user.values,
        title="<b>Total checkins per user</b>",
        color_discrete_sequence=["#0083B8"] * len(total_checkins_per_user),
        template="plotly_white"
    )
    fig_user_checkins.update_layout(
        xaxis=dict(tickmode="array", tickvals=total_checkins_per_user.index),
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=(dict(showgrid=False)),
    )

    st.plotly_chart(fig_user_hours, use_container_width=True)
    st.plotly_chart(fig_user_checkins, use_container_width=True)

st.dataframe(df_selection)

# ---- HIDE STREAMLIT STYLE ----
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)