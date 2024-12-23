import streamlit as st

st.set_page_config(page_title="Recipe Manager", page_icon="🍴")

# Custom CSS for a smaller sidebar
st.markdown(
    """
    <style>
        /* Make the sidebar narrower */
        .css-1d391kg {  /* Sidebar container */
            width: 50px;  /* Adjust this value to make the sidebar smaller */
        }

        /* Optionally, adjust the width of the main content area to match the new sidebar */
        .css-1v0mbdj {  /* Main content area */
            margin-left: 150px;  /* Adjust this to match the new sidebar width */
        }
    </style>
    """, unsafe_allow_html=True)

# Sidebar with buttons
st.sidebar.title("Navigation")
home_button = st.sidebar.button("Home")
add_recipes_button = st.sidebar.button("Add Recipes")
view_recipes_button = st.sidebar.button("View Recipes")

# Initialize the app to show the Home page by default
if not (home_button or add_recipes_button or view_recipes_button):  # When no buttons are clicked, default to Home
    home_button = True

# Handle button clicks
if home_button:
    st.title("Welcome to Recipe Manager! 🍴")
    st.markdown("""
    This app helps you manage and discover your favorite recipes.
    Use the sidebar to navigate between pages:
    - **Add Recipes**: Enter new recipes to your database.
    - **View Recipes**: Browse or search for stored recipes.
    """)

elif add_recipes_button:
    # Import and show the Add Recipes page (you can import add_recipes.py here)
    import add_recipe

elif view_recipes_button:
    # Import and show the View Recipes page (you can import view_recipes.py here)
    import view_recipes
