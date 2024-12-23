import streamlit as st
import psycopg2

# Fetch credentials from secrets
SUPABASE_USER = st.secrets["supabase"]["SUPABASE_USER"]
SUPABASE_PASSWORD = st.secrets["supabase"]["SUPABASE_PASSWORD"]
SUPABASE_HOST = st.secrets["supabase"]["SUPABASE_HOST"]
SUPABASE_PORT = st.secrets["supabase"]["SUPABASE_PORT"]
SUPABASE_DATABASE = st.secrets["supabase"]["SUPABASE_DATABASE"]

# Construct the DATABASE_URL
DATABASE_URL = f"postgres://{SUPABASE_USER}:{SUPABASE_PASSWORD}@{SUPABASE_HOST}:{SUPABASE_PORT}/{SUPABASE_DATABASE}"

# Set page title and icon
st.set_page_config(page_title="Recipe Manager", page_icon="🍴")

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

# Sidebar navigation with options
st.sidebar.title("Navigation")
page_selection = st.sidebar.radio("Choose a page", ("Home", "Recipes"))

# Home page content
if page_selection == "Home":
    st.title("Welcome to Recipe Manager! 🍴")
    st.markdown("""
    This app helps you manage and discover your favorite recipes.
    Use the sidebar to navigate between pages:
    - **Recipes**: View and add recipes to your database.
    """)

# Recipes page (Add and View Recipes combined)
elif page_selection == "Recipes":
    st.title("Manage Recipes")

    # Option to switch between Add Recipes and View Recipes
    page_option = st.radio("Choose an action", ("Add Recipe", "View Recipes"))

    if page_option == "Add Recipe":
        # Add Recipe Section
        st.subheader("Add a New Recipe")
        recipe_name = st.text_input("Recipe Name")
        ingredients = st.text_area("Ingredients")
        instructions = st.text_area("Instructions")
        meal_type = st.selectbox("Select Meal Type", ["Breakfast", "Lunch", "Dinner", "Dessert"])

        submit = st.button("Add Recipe")

        if submit:
            if recipe_name and ingredients and instructions:
                try:
                    with psycopg2.connect(DATABASE_URL) as conn:
                        with conn.cursor() as c:
                            c.execute(
                                "INSERT INTO recipes (name, ingredients, instructions, meal_type) VALUES (%s, %s, %s, %s)",
                                (recipe_name, ingredients, instructions, meal_type)
                            )
                            conn.commit()
                            st.success(f"Recipe '{recipe_name}' added successfully!")
                            st.rerun()  # Refresh the page to clear the form
                except Exception as e:
                    st.error(f"Error adding recipe: {e}")
            else:
                st.error("Please fill in all fields.")
    
    elif page_option == "View Recipes":
        # View Recipes Section
        st.subheader("View Recipes")
    
        meal_filter = st.selectbox("Filter by Meal Type", ["All", "Breakfast", "Lunch", "Dinner", "Dessert"])
    
        # Pagination control
        page = st.number_input("Page", min_value=1, step=1, key="page")
        offset = (page - 1) * 10  # Assume 10 recipes per page

        # Initialize the session state for storing selected recipe
        if "selected_recipe" not in st.session_state:
            st.session_state.selected_recipe = None

        try:
            with psycopg2.connect(DATABASE_URL) as conn:
                with conn.cursor() as c:
                    if meal_filter == "All":
                        c.execute("SELECT id, name, meal_type FROM recipes LIMIT 10 OFFSET %s", (offset,))
                    else:
                        c.execute("SELECT id, name, meal_type FROM recipes WHERE meal_type = %s LIMIT 10 OFFSET %s", (meal_filter, offset))
                    recipes = c.fetchall()

                    if recipes:
                        # Create two columns for displaying the recipes in a 2x5 grid
                        cols = st.columns(2)
                        for i, (recipe_id, recipe_name, meal_type) in enumerate(recipes):
                            col = cols[i % 2]  # Alternate between the two columns
                            if col.button(f"{recipe_name}", key=recipe_id):
                                st.session_state.selected_recipe = recipe_id  # Store the selected recipe ID

                        # Display the details of the selected recipe
                        if st.session_state.selected_recipe:
                            selected_recipe_id = st.session_state.selected_recipe
                            c.execute("SELECT name, ingredients, instructions, meal_type FROM recipes WHERE id = %s", (selected_recipe_id,))
                            recipe = c.fetchone()

                            if recipe:
                                st.subheader(f"{recipe[0]} ({recipe[3]})")
                                
                                # Ingredients
                                st.write("### Ingredients:")
                                ingredients = recipe[1].split('\n')  # Assuming ingredients are separated by newline
                                for ingredient in ingredients:
                                    if ingredient.strip():  # Avoid empty items
                                        st.markdown(f"- {ingredient.strip()}")  # Display each ingredient as a bullet point
                                
                                # Instructions
                                st.write("### Instructions:")
                                instructions = recipe[2].split('\n')  # Assuming instructions are separated by newline
                                for idx, instruction in enumerate(instructions, start=1):  # Start numbering from 1
                                    if instruction.strip():  # Avoid empty items
                                        st.markdown(f"{idx}. {instruction.strip()}")  # Display each instruction with a number
                    else:
                        st.write("No recipes found.")
        except Exception as e:
            st.error(f"Error fetching recipes: {e}")
