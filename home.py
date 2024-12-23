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
    
        try:
            with psycopg2.connect(DATABASE_URL) as conn:
                with conn.cursor() as c:
                    if meal_filter == "All":
                        c.execute("SELECT id, name, meal_type FROM recipes")
                    else:
                        c.execute("SELECT id, name, meal_type FROM recipes WHERE meal_type = %s", (meal_filter,))
                    recipes = c.fetchall()
    
                    if recipes:
                        # Create a 5x2 grid layout (5 columns per row, 2 rows per page)
                        num_cols = 5
                        num_rows = 2
                        columns = st.columns(num_cols)  # Create 5 columns in the layout
    
                        for i, (recipe_id, recipe_name, meal_type) in enumerate(recipes):
                            col = columns[i % num_cols]  # Cycle through columns
    
                            with col:
                                if st.button(f"{recipe_name}", key=recipe_id):
                                    c.execute("SELECT ingredients, instructions FROM recipes WHERE id = %s", (recipe_id,))
                                    recipe = c.fetchone()
                                    if recipe:
                                        st.subheader(f"{recipe_name} ({meal_type})")
    
                                        # Ingredients
                                        st.write("### Ingredients:")
                                        ingredients = recipe[0].split('\n')  # Assuming ingredients are separated by newline
                                        for ingredient in ingredients:
                                            if ingredient.strip():  # Avoid empty items
                                                st.markdown(f"- {ingredient.strip()}")  # Display each ingredient as a bullet point
    
                                        # Instructions
                                        st.write("### Instructions:")
                                        instructions = recipe[1].split('\n')  # Assuming instructions are separated by newline
                                        for idx, instruction in enumerate(instructions, start=1):  # Start numbering from 1
                                            if instruction.strip():  # Avoid empty items
                                                st.markdown(f"{idx}. {instruction.strip()}")  # Display each instruction with a number
                    else:
                        st.write("No recipes found.")
        except Exception as e:
            st.error(f"Error fetching recipes: {e}")
