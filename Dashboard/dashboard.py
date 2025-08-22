import pandas as pd
import plotly.express as px
import streamlit as st

# Set page configuration
st.set_page_config(
    page_title="E-Commerce Analytics Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS Styling ---
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# --- Data Loading and Caching ---
@st.cache_data
def load_data(data_path='./data/'):
    """
    Loads all necessary CSV files and performs initial merges.
    Assumes CSV files are in a 'data' folder one level above the dashboard script.
    """
    customers_df = pd.read_csv(data_path + 'customers_dataset.csv')
    orders_df = pd.read_csv(data_path + 'orders_dataset.csv')
    order_items_df = pd.read_csv(data_path + 'order_items_dataset.csv')
    products_df = pd.read_csv(data_path + 'products_dataset.csv')
    product_translation_df = pd.read_csv(data_path + 'product_category_name_translation.csv')
    payments_df = pd.read_csv(data_path + 'order_payments_dataset.csv')

    # Merge for sales by category analysis
    order_products_df = pd.merge(order_items_df, products_df, on='product_id', how='inner')
    sales_by_category_df = pd.merge(order_products_df, product_translation_df, on='product_category_name', how='inner')

    # Merge for customer demographics analysis
    customer_orders_df = pd.merge(orders_df, customers_df, on='customer_id', how='inner')
    
    # Merge for payment analysis
    payment_details_df = pd.merge(orders_df, payments_df, on='order_id', how='inner')
    
    # Merge for RFM analysis
    rfm_df = pd.merge(orders_df, customers_df, on='customer_id')
    rfm_df = pd.merge(rfm_df, payments_df, on='order_id')

    return sales_by_category_df, customer_orders_df, payment_details_df, rfm_df

# --- Analysis Functions ---
@st.cache_data
def get_sales_by_category(df):
    category_sales = df['product_category_name_english'].value_counts().reset_index()
    category_sales.columns = ['category', 'sales_count']
    return category_sales.head(10), category_sales.tail(10).sort_values(by='sales_count', ascending=True)

@st.cache_data
def get_customer_demographics(df):
    customers_by_state = df['customer_state'].value_counts().head(10).reset_index()
    customers_by_state.columns = ['state', 'customer_count']
    return customers_by_state

@st.cache_data
def get_payment_methods(df):
    payments_by_type = df['payment_type'].value_counts().reset_index()
    payments_by_type.columns = ['payment_type', 'transaction_count']
    return payments_by_type

@st.cache_data
def calculate_rfm(df):
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    
    rfm = df.groupby('customer_unique_id', as_index=False).agg({
        'order_purchase_timestamp': 'max',
        'order_id': 'nunique',
        'payment_value': 'sum'
    })
    rfm.columns = ['customer_unique_id', 'max_purchase_date', 'frequency', 'monetary']

    snapshot_date = rfm['max_purchase_date'].max() + pd.Timedelta(days=1)
    rfm['recency'] = (snapshot_date - rfm['max_purchase_date']).dt.days
    
    rfm['R_score'] = pd.qcut(rfm['recency'], 4, labels=[4, 3, 2, 1])
    rfm['F_score'] = pd.qcut(rfm['frequency'].rank(method='first'), 4, labels=[1, 2, 3, 4])
    rfm['M_score'] = pd.qcut(rfm['monetary'], 4, labels=[1, 2, 3, 4])
    
    rfm['Segment_RF'] = rfm['R_score'].astype(str) + rfm['F_score'].astype(str)
    
    seg_map = {
        r'^[3-4][3-4]': 'Champions', r'^[3-4]2': 'Potential Loyalists',
        r'^[3-4]1': 'New Customers', r'^2[3-4]': 'Loyal Customers',
        r'^22': 'Need Attention', r'^21': 'About to Sleep',
        r'^1[3-4]': 'At Risk', r'^1[1-2]': 'Hibernating'
    }
    rfm['Segment'] = rfm['Segment_RF'].replace(seg_map, regex=True)
    
    segment_counts = rfm['Segment'].value_counts().reset_index()
    segment_counts.columns = ['segment', 'customer_count']
    
    return segment_counts

# --- Load Data ---
sales_df, customers_df, payments_df, rfm_base_df = load_data()

# --- Sidebar ---
with st.sidebar:
    st.title("Proyek Analisis Data")
    st.markdown("**• Nama:** Sakti Kusuma Aji")
    st.markdown("**• Email:** skarluajitkas@gmail.com")
    st.markdown("---")
    st.markdown(
        "Dashboard ini menyajikan analisis data dari E-Commerce Public Dataset. "
        "Fokus analisis meliputi performa penjualan produk, demografi pelanggan, "
        "dan segmentasi pelanggan menggunakan metode RFM."
    )

# --- Main Dashboard ---
st.title("🛒 E-Commerce Analytics Dashboard")
st.markdown("---")

# Key Metrics
total_revenue = payments_df['payment_value'].sum()
total_orders = payments_df['order_id'].nunique()
total_customers = customers_df['customer_unique_id'].nunique()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="**Total Revenue**", value=f"R$ {total_revenue:,.2f}")
with col2:
    st.metric(label="**Total Orders**", value=f"{total_orders:,}")
with col3:
    st.metric(label="**Total Customers**", value=f"{total_customers:,}")

st.markdown("---")

# --- Visualizations ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏆 Performa Penjualan Berdasarkan Kategori")
    top_categories_df, bottom_categories_df = get_sales_by_category(sales_df)
    
    fig_top = px.bar(
        top_categories_df,
        x='sales_count',
        y='category',
        orientation='h',
        title='<b>Top 10 Kategori Terlaris</b>',
        labels={'sales_count': 'Jumlah Penjualan', 'category': 'Kategori'},
        color='sales_count',
        color_continuous_scale=px.colors.sequential.Viridis
    )
    fig_top.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_top, use_container_width=True)

    fig_bottom = px.bar(
        bottom_categories_df,
        x='sales_count',
        y='category',
        orientation='h',
        title='<b>Top 10 Kategori Kurang Laris</b>',
        labels={'sales_count': 'Jumlah Penjualan', 'category': 'Kategori'},
        color='sales_count',
        color_continuous_scale=px.colors.sequential.Plasma_r
    )
    fig_bottom.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_bottom, use_container_width=True)

with col2:
    st.subheader("🌍 Demografi Pelanggan & Metode Pembayaran")
    
    state_demographics_df = get_customer_demographics(customers_df)
    fig_state = px.bar(
        state_demographics_df,
        x='customer_count',
        y='state',
        orientation='h',
        title='<b>Top 10 Negara Bagian Berdasarkan Jumlah Pelanggan</b>',
        labels={'customer_count': 'Jumlah Pelanggan', 'state': 'Negara Bagian'},
        color='customer_count',
        color_continuous_scale=px.colors.sequential.Cividis_r
    )
    fig_state.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_state, use_container_width=True)

    payment_methods_df = get_payment_methods(payments_df)
    fig_payment = px.pie(
        payment_methods_df,
        names='payment_type',
        values='transaction_count',
        title='<b>Distribusi Metode Pembayaran</b>',
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    st.plotly_chart(fig_payment, use_container_width=True)

st.markdown("---")
st.subheader("🧩 Segmentasi Pelanggan (RFM Analysis)")
rfm_segments_df = calculate_rfm(rfm_base_df)
fig_rfm = px.bar(
    rfm_segments_df,
    x='customer_count',
    y='segment',
    orientation='h',
    title='<b>Distribusi Pelanggan Berdasarkan Segmen RFM</b>',
    labels={'customer_count': 'Jumlah Pelanggan', 'segment': 'Segmen'},
    color='customer_count',
    color_continuous_scale=px.colors.sequential.Cividis_r
)
fig_rfm.update_layout(yaxis={'categoryorder':'total ascending'})
st.plotly_chart(fig_rfm, use_container_width=True)

st.caption("Copyright © 2024 - Dibuat oleh Sakti Kusuma Aji")