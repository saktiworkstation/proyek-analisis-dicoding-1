import pandas as pd
import plotly.express as px
import streamlit as st
from pathlib import Path

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="E-Commerce Analytics Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- FUNGSI UNTUK MEMUAT DATA (DENGAN CACHING) ---
@st.cache_data
def load_and_prepare_data(data_path):
    base_path = Path(data_path)

    # Memuat dataset utama
    customers_df = pd.read_csv(base_path / 'customers_dataset.csv')
    orders_df = pd.read_csv(base_path / 'orders_dataset.csv')
    order_items_df = pd.read_csv(base_path / 'order_items_dataset.csv')
    products_df = pd.read_csv(base_path / 'products_dataset.csv')
    product_translation_df = pd.read_csv(base_path / 'product_category_name_translation.csv')
    payments_df = pd.read_csv(base_path / 'order_payments_dataset.csv')
    reviews_df = pd.read_csv(base_path / 'order_reviews_dataset.csv')

    # Membersihkan data produk
    products_df.dropna(subset=['product_category_name'], inplace=True)

    # Gabungkan data
    main_df = orders_df.merge(customers_df, on='customer_id', how='left')
    main_df = main_df.merge(order_items_df, on='order_id', how='left')
    main_df = main_df.merge(payments_df, on='order_id', how='left')
    main_df = main_df.merge(products_df, on='product_id', how='left')
    main_df = main_df.merge(product_translation_df, on='product_category_name', how='left')
    main_df = main_df.merge(reviews_df[['order_id', 'review_score']], on='order_id', how='left')

    # Konversi tanggal
    main_df['order_purchase_timestamp'] = pd.to_datetime(main_df['order_purchase_timestamp'])
    main_df.dropna(subset=['product_category_name_english', 'price', 'freight_value'], inplace=True)

    return main_df


# --- LOAD DATA ---
try:
    main_df = load_and_prepare_data('data/')
except FileNotFoundError:
    st.error("❌ Folder 'data' tidak ditemukan. Pastikan struktur folder Anda benar.")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.subheader("👤 Data Diri")
    st.markdown("**• Nama:** Sakti Kusuma Aji")
    st.markdown("**• Email:** skarluajitkas@gmail.com")
    st.markdown("**• ID Dicoding:** saktikusumaaji")
    st.markdown("---")

    st.header("⚙️ Filter Interaktif")

    # Rentang waktu
    min_date = main_df["order_purchase_timestamp"].min().date()
    max_date = main_df["order_purchase_timestamp"].max().date()
    date_range = st.date_input(
        "📅 Pilih Rentang Waktu",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )

    if isinstance(date_range, tuple) or isinstance(date_range, list):
        start_date, end_date = date_range
    else:
        start_date, end_date = min_date, max_date

    # Kategori produk
    all_categories = sorted(main_df['product_category_name_english'].dropna().unique())
    selected_categories = st.multiselect(
        "📦 Pilih Kategori Produk",
        options=all_categories,
        default=all_categories
    )

# --- FILTER DATA ---
filtered_df = main_df[
    (main_df["order_purchase_timestamp"].dt.date >= start_date) &
    (main_df["order_purchase_timestamp"].dt.date <= end_date) &
    (main_df["product_category_name_english"].isin(selected_categories))
]

# --- HALAMAN UTAMA ---
st.title("🛒 E-Commerce Analytics Dashboard")
st.markdown(f"Data dari **{start_date.strftime('%d %B %Y')}** hingga **{end_date.strftime('%d %B %Y')}**")
st.markdown("Dashboard ini menyajikan analisis data dari E-Commerce Public Dataset. Fokus analisis meliputi performa penjualan produk, demografi pelanggan, dan segmentasi pelanggan menggunakan metode RFM.")
st.markdown("---")

# --- METRIK UTAMA ---
if not filtered_df.empty:
    total_revenue = filtered_df['payment_value'].sum()
    total_orders = filtered_df['order_id'].nunique()
    total_customers = filtered_df['customer_unique_id'].nunique()
    avg_review_score = filtered_df['review_score'].mean()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Total Pendapatan", f"R$ {total_revenue:,.2f}")
    col2.metric("📄 Total Pesanan", f"{total_orders:,}")
    col3.metric("👥 Total Pelanggan", f"{total_customers:,}")
    col4.metric("⭐ Rata-rata Review", f"{avg_review_score:.2f}")
else:
    st.warning("⚠️ Tidak ada data sesuai filter.")

st.markdown("---")

# --- VISUALISASI ---
if not filtered_df.empty:
    col1, col2 = st.columns(2)

    with col1:
        # Top kategori
        st.subheader("🏆 Top 10 Kategori Produk")
        category_sales = filtered_df['product_category_name_english'].value_counts().nlargest(10).reset_index()
        category_sales.columns = ['category', 'sales_count']
        fig_top_cat = px.bar(
            category_sales, x='sales_count', y='category', orientation='h',
            color='sales_count', template='plotly_dark',
            color_continuous_scale=px.colors.sequential.Aggrnyl
        ).update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_top_cat, use_container_width=True)

    with col2:
        # Demografi pelanggan
        st.subheader("🌍 Top 10 Negara Bagian")
        state_demographics = filtered_df.groupby('customer_state')['customer_unique_id'].nunique().nlargest(10).reset_index()
        state_demographics.columns = ['state', 'customer_count']
        fig_state = px.bar(
            state_demographics, x='customer_count', y='state', orientation='h',
            color='customer_count', template='plotly_dark',
            color_continuous_scale=px.colors.sequential.Blues_r
        ).update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_state, use_container_width=True)

    # Time series revenue
    st.subheader("📈 Tren Pendapatan Harian")
    daily_sales = filtered_df.groupby(filtered_df['order_purchase_timestamp'].dt.date)['payment_value'].sum().reset_index()
    fig_trend = px.line(
        daily_sales, x='order_purchase_timestamp', y='payment_value',
        markers=True, template='plotly_dark'
    )
    fig_trend.update_layout(yaxis_title="Revenue", xaxis_title="Tanggal")
    st.plotly_chart(fig_trend, use_container_width=True)

    # Metode pembayaran
    st.subheader("💳 Distribusi Metode Pembayaran")
    payment_methods = filtered_df['payment_type'].value_counts().reset_index()
    payment_methods.columns = ['type', 'count']
    fig_payment = px.pie(
        payment_methods, names='type', values='count',
        hole=0.5, color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_payment.update_layout(template='plotly_dark')
    st.plotly_chart(fig_payment, use_container_width=True)

else:
    st.info("Silakan pilih filter berbeda untuk melihat data.")

st.caption("📌 Copyright © 2025 - Dibuat oleh Sakti Kusuma Aji")