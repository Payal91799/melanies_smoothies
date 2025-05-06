# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col

# Title and description
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the Fruits you want in your Smoothie!")

# Name input
name_on_order = st.text_input('Name on Smoothie:')
st.write('The current movie title is', name_on_order)

# Cache the Snowflake connection
@st.cache_resource
def get_snowflake_session():
    cnx = st.connection("snowflake")
    return cnx.session()

session = get_snowflake_session()

# Get fruit options
fruit_df = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
fruit_names = [row['FRUIT_NAME'] for row in fruit_df.collect()]

# Multiselect for ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_names,
    max_selections=5
)

# If ingredients are selected
if ingredients_list:
    ingredients_string = ' '.join(ingredients_list)

    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    #st.write(my_insert_stmt)

    if st.button('Submit Order'):
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
