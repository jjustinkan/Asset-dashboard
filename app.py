import streamlit as st
import pandas as pd
import plotly.express as px
import requests

st.set_page_config(page_title="全球資產動態戰情室", layout="wide", page_icon="🛡️")
st.title("🛡️ 全球跨國資產動態戰情室 (Daily Dashboard)")

API_URL = "https://script.google.com/macros/s/AKfycbzL4DygHMMAQUD9kNltumc3K9UKuwp7i3gC40bGqjJe_qWmMYN9ipksOdrvONyuC-a-/exec"

@st.cache_data(ttl=600)  # 縮短快取時間至10分鐘以利即時校正
def load_data():
    res = requests.get(API_URL)
    df = pd.DataFrame(res.json())
    
    # 數據清洗：確保數值解析正確
    df['現值TWD'] = pd.to_numeric(df['現值TWD'], errors='coerce').fillna(0)
    df['股數'] = pd.to_numeric(df['股數'], errors='coerce').fillna(0)
    
    # 僅過濾真正為 0 的無效列，保留所有有效資產
    df = df[df['現值TWD'] > 0]
    return df

try:
    df = load_data()

    total_nav = df['現值TWD'].sum()
    
    # 精確定義股票與廣義固定收益 (含債券與特別股)
    equity_df = df[df['類別'] == '股票']
    fixed_income_df = df[df['類別'].isin(['債券', '特別股'])]
    
    equity_nav = equity_df['現值TWD'].sum()
    fixed_income_nav = fixed_income_df['現值TWD'].sum()
    us_equity_nav = equity_df[equity_df['國家'] == 'US']['現值TWD'].sum()

    # 頂部戰情卡片 (校正後 logic)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("總資產現值 (TWD)", f"${total_nav:,.0f}")
    col2.metric("股票配置比例", f"{(equity_nav/total_nav)*100:.1f}%" if total_nav > 0 else "0%")
    col3.metric("固定收益比例 (含特別股)", f"{(fixed_income_nav/total_nav)*100:.1f}%" if total_nav > 0 else "0%")
    col4.metric("股票-美股暴險", f"{(us_equity_nav/equity_nav)*100:.1f}%" if equity_nav > 0 else "0%")

    st.markdown("---")

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("📊 大類資產配置比例")
        fig_asset = px.pie(
            df, values='現值TWD', names='類別', hole=0.45,
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        st.plotly_chart(fig_asset, use_container_width=True)

    with c2:
        st.subheader("🌍 股票國家暴險 (National Exposure)")
        fig_geo = px.pie(
            equity_df, values='現值TWD', names='國家', hole=0.45,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig_geo, use_container_width=True)

    st.markdown("---")
    st.subheader("🏦 各機構資產明細清單")
    st.dataframe(df[['機構', '代碼', '名稱', '類別', '國家', '股數', '現值TWD']], use_container_width=True)

except Exception as e:
    st.error(f"資料連接失敗，請檢查 API URL 配置：{e}")
