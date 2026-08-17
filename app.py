import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# 1. 頁面基礎配置
st.set_page_config(page_title="全球資產動態戰情室", layout="wide", page_icon="🛡️")
st.title("🛡️ 全球跨國資產動態戰情室 (Daily Dashboard)")

# 2. 貼入第二階段取得的 API URL
API_URL = "https://script.google.com/macros/s/AKfycbzL4DygHMMAQUD9kNltumc3K9UKuwp7i3gC40bGqjJe_qWmMYN9ipksOdrvONyuC-a-/exec"

@st.cache_data(ttl=1800)  # 每半小時自動更新快取
def load_data():
    res = requests.get(API_URL)
    df = pd.DataFrame(res.json())
    df['現值 (TWD)'] = pd.to_numeric(df['現值 (TWD)'])
    return df

try:
    df = load_data()

    # 3. 核心 KPI 數據計算
    total_nav = df['現值 (TWD)'].sum()
    equity_df = df[df['類別'] == '股票']
    bond_df = df[df['類別'] == '債券']
    
    equity_nav = equity_df['現值 (TWD)'].sum()
    bond_nav = bond_df['現值 (TWD)'].sum()
    us_equity_nav = equity_df[equity_df['國家'] == 'US']['現值 (TWD)'].sum()

    # 頂部戰情卡片
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("總資產現值 (TWD)", f"${total_nav:,.0f}")
    col2.metric("股票配置比例", f"{(equity_nav/total_nav)*100:.1f}%")
    col3.metric("固定收益比例", f"{(bond_nav/total_nav)*100:.1f}%")
    col4.metric("股票-美股暴險", f"{(us_equity_nav/equity_nav)*100:.1f}%")

    st.markdown("---")

    # 4. 圖表視覺化
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("📊 大類資產配置比例")
        fig_asset = px.pie(
            df, values='現值 (TWD)', names='類別', hole=0.45,
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        st.plotly_chart(fig_asset, use_container_width=True)

    with c2:
        st.subheader("🌍 股票國家暴險 (National Exposure)")
        fig_geo = px.pie(
            equity_df, values='現值 (TWD)', names='國家', hole=0.45,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig_geo, use_container_width=True)

    # 5. 明細數據表
    st.markdown("---")
    st.subheader("🏦 各機構資產明細清單")
    st.dataframe(df[['機構', '代碼', '名稱', '類別', '國家', '股數', '現值 (TWD)']], use_container_width=True)

except Exception as e:
    st.error(f"資料連接失敗，請檢查 API URL 配置：{e}")
