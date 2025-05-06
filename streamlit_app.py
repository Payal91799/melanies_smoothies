# Import required libraries
import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col

# App header
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the Fruits you want in your Smoothie!")

# Input: name on order
name_on_order = st.text_input('Name on Smoothie:')

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Query fruit options from Snowflake
my_dataframe = session.table('smoothies.public.fruit_options').select(
    col('FRUIT_NAME'), col('SEARCH_ON')
)

# Convert to Pandas for easier manipulation
pd_df = my_dataframe.to_pandas()
st.write("DataFrame preview:")
st.dataframe(pd_df)

# Multiselect widget for ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

# If ingredients are selected, show their nutrition info
if ingredients_list:
    ingredients_string = ''
    
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        
        # Get search value for API
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        
        # Display section header
        st.subheader(f"{fruit_chosen} Nutrition Information")
        
        # Fetch from fruityvice API
        response = requests.get(f"https://fruityvice.com/api/fruit/{search_on}")
        
        if response.status_code == 200:
            data = pd.json_normalize(response.json())
            st.dataframe(data, use_container_width=True)
        else:
            st.error(f"Could not load data for {fruit_chosen}")

    # Order submission section
    if st.button('Submit Order'):
        insert_stmt = f"""
            INSERT INTO smoothies.public.orders(ingredients, name_on_order)
            VALUES ('{ingredients_string.strip()}', '{name_on_order}')
        """
        session.sql(insert_stmt).collect()
        st.success("Your Smoothie is ordered!", icon="✅")
