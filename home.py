import streamlit as st

# Custom CSS for a smaller sidebar
st.markdown(
    """
    <style>
        /* Make the sidebar narrower */
        .css-1d391kg {  /* Sidebar container */
            width: 150px;  /* Adjust this value to make the sidebar smaller */
        }

        /* Optionally, adjust the width of the main content area to match the new sidebar */
        .css-1v0mbdj {  /* Main content area */
            margin-left: 150px;  /* Adjust this to match the new sidebar width */
        }
    </style>
    """, unsafe_allow_html=True)

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
