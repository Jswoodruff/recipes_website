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
                    # Capitalize the recipe name and split ingredients and instructions for capitalization
                    recipe_name = recipe_name.strip().capitalize()  # Capitalize the recipe name

                    # Capitalize each line in ingredients and instructions
                    ingredients = "\n".join([ingredient.strip().capitalize() for ingredient in ingredients.split("\n") if ingredient.strip()])
                    instructions = "\n".join([instruction.strip().capitalize() for instruction in instructions.split("\n") if instruction.strip()])

                    with psycopg2.connect(DATABASE_URL) as conn:
                        with conn.cursor() as c:
                            c.execute(
                                "INSERT INTO recipes (name, ingredients, instructions, meal_type) VALUES (%s, %s, %s, %s)",
                                (recipe_name, ingredients, instructions, meal_type)
                            )
                            conn.commit()
                            st.success(f"Recipe '{recipe_name}' added successfully!")
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
                        # Create a 5-column grid for recipe names
                        columns = st.columns(5)  # 5 columns for the grid
                        current_column = 0  # Track the current column in the grid
    
                        recipe_selected = None  # Track the selected recipe
                    
                        for recipe_id, recipe_name, meal_type in recipes:
                            if current_column == 5:  # Reset the column to 0 after 5 items
                                current_column = 0
    
                            with columns[current_column]:
                                # Button for each recipe
                                if st.button(f"{recipe_name}", key=recipe_id):
                                    recipe_selected = recipe_id  # Track the selected recipe
                            
                            current_column += 1  # Move to the next column
                        
                        # If a recipe is selected, show the detailed view
                        if recipe_selected:
                            # Fetch the selected recipe details
                            with psycopg2.connect(DATABASE_URL) as conn:
                                with conn.cursor() as c:
                                    c.execute("SELECT name, ingredients, instructions, meal_type FROM recipes WHERE id = %s", (recipe_selected,))
                                    recipe = c.fetchone()
                                    if recipe:
                                        recipe_name, ingredients, instructions, meal_type = recipe
                                        
                                        st.subheader(f"{recipe_name} ({meal_type})")
                                        
                                        # Ingredients
                                        st.write("### Ingredients:")
                                        ingredients = ingredients.split('\n')  # Assuming ingredients are separated by newline
                                        for ingredient in ingredients:
                                            if ingredient.strip():  # Avoid empty items
                                                st.markdown(f"- {ingredient.strip()}")  # Display each ingredient as a bullet point
                                        
                                        # Instructions
                                        st.write("### Instructions:")
                                        instructions = instructions.split('\n')  # Assuming instructions are separated by newline
                                        for idx, instruction in enumerate(instructions, start=1):  # Start numbering from 1
                                            if instruction.strip():  # Avoid empty items
                                                st.markdown(f"{idx}. {instruction.strip()}")  # Display each instruction with a number
    
                    else:
                        st.write("No recipes found.")
        except Exception as e:
            st.error(f"Error fetching recipes: {e}")
    