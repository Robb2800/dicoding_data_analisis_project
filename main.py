import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import unidecode
import requests
import os


file_links = [
    "https://drive.google.com/uc?id=1xMxVMSDbTDCX2M_ds-RSgeGTo6vF9zlR",
    "https://drive.google.com/uc?id=1mXtntj-lgnuoiygNtBT5nKH6tA5EZK9q",
    "https://drive.google.com/uc?id=1_HQlq-6Y_PR6QF-ghhdk1zXLdsUoQOsS"
]

# Download and cache files
@st.cache_data
def fetch_file(url, file_name):
    response = requests.get(url)
    with open(file_name, "wb") as f:
        f.write(response.content)
    return file_name

def load_df(filepath):
    df = pd.read_csv(filepath)
    return df

def customer_distribution(df):
    cus_geo_df = df

    # Aggregating customer count by city and state
    cust_geo_counts = cus_geo_df.groupby(['geolocation_state', 'geolocation_city'], as_index=False).agg(
        customer_count=('customer_id', 'count'),
        geolocation_lat=('geolocation_lat', 'mean'),
        geolocation_lng=('geolocation_lng', 'mean')
    )
    return cust_geo_counts

def seller_distribution(df):
   seller_geo_df = df
   
   seller_geo_counts = seller_geo_df.groupby(['geolocation_state', 'geolocation_city'], as_index=False).agg(
        seller_count=('seller_id', 'count'),
        geolocation_lat=('geolocation_lat', 'mean'),
        geolocation_lng=('geolocation_lng', 'mean')
    )
   return seller_geo_counts

def installment_analysis(df):
  
    cust_orders_payments_merge = df
    installment_data = cust_orders_payments_merge[cust_orders_payments_merge['payment_type'] == 'credit_card']
    city_installments = installment_data.groupby(['geolocation_state', 'geolocation_city']).agg(
            avg_installments=('payment_installments', 'mean'),
            installment_transactions=('payment_installments', 'size'),
            geolocation_lat=('geolocation_lat', 'mean'),
            geolocation_lng=('geolocation_lng', 'mean')
    ).reset_index()

    city_totals = installment_data.groupby(['geolocation_state', 'geolocation_city']).size().reset_index(name='total_transactions')
    city_analysis = city_installments.merge(city_totals, on=['geolocation_state', 'geolocation_city'])
    city_analysis['installment_tendency'] = (city_analysis['installment_transactions'] / city_analysis['total_transactions']) * 100
    return city_analysis  

def main():
   
   st.title('Proyek Analisis Data: E-Commerce Public Dataset')

   st.subheader('Nama: Kevin Robert Siswoyo')
   st.subheader('Email: kevin.siswoyo28@gmail.com')
   st.subheader('ID Dicoding: kevinrob28')

   st.write("### Downloading and Preparing Data...")
   local_files = []
   for i, url in enumerate(file_links):
        file_name = f"file_{i + 1}.csv"
        st.write(f"Downloading: {file_name}")
        local_file = fetch_file(url, file_name)
        local_files.append(local_file)
    
   st.text("")
   st.markdown("***")

   
# Customer Distribution
   st.write('## Customer and Seller Distribution')
   cus_geo_df = load_df(local_files[0])
   cust_geo_counts = customer_distribution(cus_geo_df)
  
   top_cities = cust_geo_counts.groupby(by='geolocation_city').sum().sort_values(by='customer_count', ascending=False).head(10).reset_index()
   fig, ax = plt.subplots(figsize=(20, 12))
   sns.barplot(data=top_cities, x='customer_count', y='geolocation_city', palette='viridis', ax=ax)
   ax.set_xlabel('Customer Count')
   ax.set_ylabel('City')
   ax.tick_params(axis='x', labelsize=35)
   ax.tick_params(axis='y', labelsize=30)
   st.text("Top 10 Cities by Customer Count")
   st.pyplot(fig, use_container_width=True)

   cust_geo_counts['log_cust_count'] = np.log1p(cust_geo_counts['customer_count'])
   heatmap_data = cust_geo_counts[['geolocation_lat', 'geolocation_lng', 'log_cust_count']].dropna().values.tolist()
   map_cust = folium.Map(location=[-14.2350, -51.9253], zoom_start=4)
   HeatMap(heatmap_data, radius=10, blur=12).add_to(map_cust)
   st.text("Customer Distribution Heatmap")
   st_folium(map_cust, width=800, height=400)

   
    
# Seller Distribution
   seller_geo_df = load_df(local_files[1])
   seller_geo_counts = seller_distribution(seller_geo_df)

   top_cities = seller_geo_counts.groupby(by='geolocation_city').sum().sort_values(by='seller_count', ascending=False).head(10).reset_index()
   fig, ax = plt.subplots(figsize=(20, 12))
   sns.barplot(data=top_cities, x='seller_count', y='geolocation_city', palette='viridis', ax=ax)
   ax.set_xlabel('Seller Count')
   ax.set_ylabel('City')
   ax.tick_params(axis='x', labelsize=35)
   ax.tick_params(axis='y', labelsize=30)
   st.text("Top 10 Cities by Seller Count")
   st.pyplot(fig, use_container_width=True)

   seller_geo_counts['log_seller_count'] = np.log1p(seller_geo_counts['seller_count'])
   heatmap_data = seller_geo_counts[['geolocation_lat', 'geolocation_lng', 'log_seller_count']].dropna().values.tolist()
   map_seller = folium.Map(location=[-14.2350, -51.9253], zoom_start=4)
   HeatMap(heatmap_data, radius=10, blur=12).add_to(map_seller)
   st.text("Seller Distribution Heatmap")
   st_folium(map_seller, width=800, height=400)

    


# Installment Analysis
   st.write('## Installment Analysis')
   cust_orders_payments_merge = load_df(local_files[2])
   city_analysis = installment_analysis(cust_orders_payments_merge)
   st.text('Top 10 Cities with High Installment Tendency (Weighted by Transactions)')
   top_cities_installments = city_analysis.sort_values(by='installment_tendency', ascending=False).head(10)


   plt.figure(figsize=(10, 6))
   sns.barplot(data=top_cities_installments, x='installment_tendency', y='geolocation_city', hue='installment_transactions', palette='Blues_d')
   plt.xlabel('Installment Tendency (%)')
   plt.ylabel('City')
   plt.tick_params(axis='x', labelsize=35)
   plt.tick_params(axis='y', labelsize=30)
   st.pyplot(plt)

   heatmap_data = city_analysis[['geolocation_lat', 'geolocation_lng', 'installment_tendency']].dropna()
   map_ins = folium.Map(location=[-14.2350, -51.9253], zoom_start=4)
   HeatMap(heatmap_data.values, radius=10, blur=12, max_zoom=1).add_to(map_ins)
   st.text("Credit Card Usage Distribution Heatmap")
   st_folium(map_ins, width=800, height=400)
   

   st.caption('By Kevin Robert Siswoyo - kevin.siswoyo28@gmail.com -  2024')
if __name__ == "__main__":
    main()