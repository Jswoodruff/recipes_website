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
        /* Style for text inputs */
        .streamlit-expanderHeader, .css-1v0mbdj, .css-1d391kg, .stTextInput input, .stTextArea textarea {
            background-color: #d3d3d3;  /* Light grey background */
            color: #000000;  /* Black text */
            border: 1px solid #ccc;  /* Light grey border */
            padding: 10px;  /* Padding inside the input box */
            border-radius: 5px;  /* Rounded corners for a smoother look */
        }
        
        /* Style for select box */
        .stSelectbox select {
            background-color: #d3d3d3;
            color: #d3d3d3;
            border: 1px solid #ccc;
            padding: 10px;
            border-radius: 5px;
        }
    </style>
    """, unsafe_allow_html=True)

# Sidebar navigation with options
st.sidebar.title("Navigation")
page_selection = st.sidebar.radio("Choose a page", ("Home", "Recipes"))

# Home page content
if page_selection == "Home":
    st.title("Welcome to Your Recipe Book! 🍴")


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
                    for recipe_id, recipe_name, meal_type in recipes:
                        # Button for viewing and editing the recipe
                        if st.button(f"Edit {recipe_name}", key=recipe_id):
                            # Fetch the current details of the selected recipe
                            c.execute("SELECT name, ingredients, instructions, meal_type FROM recipes WHERE id = %s", (recipe_id,))
                            recipe = c.fetchone()

                            # If recipe details are found, display the fields for editing
                            if recipe:
                                st.write(f"Editing: {recipe_name} ({meal_type})")
                                
                                # Input fields pre-filled with current recipe data
                                updated_name = st.text_input("Recipe Name", value=recipe[0])
                                updated_ingredients = st.text_area("Ingredients", value=recipe[1])
                                updated_instructions = st.text_area("Instructions", value=recipe[2])
                                updated_meal_type = st.selectbox("Select Meal Type", ["Breakfast", "Lunch", "Dinner", "Dessert"], index=["Breakfast", "Lunch", "Dinner", "Dessert"].index(recipe[3]))

                                # Update button to save the changes
                                update_submit = st.button("Update Recipe", key=f"update_{recipe_id}")

                                if update_submit:
                                    # Update the recipe in the database
                                    try:
                                        with psycopg2.connect(DATABASE_URL) as update_conn:
                                            with update_conn.cursor() as update_cursor:
                                                update_cursor.execute("""
                                                    UPDATE recipes
                                                    SET name = %s, ingredients = %s, instructions = %s, meal_type = %s
                                                    WHERE id = %s
                                                """, (updated_name, updated_ingredients, updated_instructions, updated_meal_type, recipe_id))
                                                update_conn.commit()
                                                st.success(f"Recipe '{updated_name}' updated successfully!")
                                    except Exception as e:
                                        st.error(f"Error updating recipe: {e}")

                else:
                    st.write("No recipes found.")
    except Exception as e:
        st.error(f"Error fetching recipes: {e}")
