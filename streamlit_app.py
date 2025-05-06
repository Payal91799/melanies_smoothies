# Import python packages
import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the Fruits you want in your Smoothie!")

name_on_order = st.text_input('Name on Smoothie:')
st.write('The current movie title is', name_on_order)

# Snowflake connection and table fetch
cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table('smoothies.public.fruit_options').select(
    col('FRUIT_NAME'), col('SEARCH_ON')
)

# Convert to pandas
pd_df = my_dataframe.to_pandas()
st.dataframe(pd_df)

  if st.button('Submit Order'):
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
      
# Ingredient selector
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

if ingredients_list:
    ingredients_string = ' '.join(ingredients_list)

    for fruit_chosen in ingredients_list:
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]

        st.subheader(f"{fruit_chosen} Nutrition Information")
        
        # Fruityvice API
        try:
            fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{search_on.lower()}")
            st.dataframe(data=fruityvice_response.json(), use_container_width=True)
        except Exception as e:
            st.error(f"Fruityvice API failed for {fruit_chosen}: {e}")

        # Smoothiefroot API
        try:
            smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on.lower()}")
            st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
        except Exception as e:
            st.error(f"Smoothiefroot API failed for {fruit_chosen}: {e}")

    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

  
