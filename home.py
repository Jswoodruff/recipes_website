import streamlit as st

# Sidebar navigation
page = st.sidebar.selectbox("Choose a page", ["Home", "Add Recipes", "View Recipes"])

if page == "Home":
    st.title("Welcome to Recipe Manager! 🍴")
    st.markdown("""
    This app helps you manage and discover your favorite recipes.
    Use the sidebar to navigate between pages:
    - **Add Recipes**: Enter new recipes to your database.
    - **View Recipes**: Browse or search for stored recipes.
    """)

elif page == "Add Recipes":
    # Add Recipes code (you can import the add_recipes.py code here)
    import add_recipes

elif page == "View Recipes":
    # View Recipes code (you can import the view_recipes.py code here)
    import view_recipes
