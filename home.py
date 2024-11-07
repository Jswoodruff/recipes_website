import streamlit as st
import psycopg2
from dotenv import load_dotenv
import os

# Full path to your .env file
current_dir = os.getcwd()
st.write(f"Current working directory: {current_dir}")

# Set the path to the .env file
dotenv_path = os.path.join(current_dir, '.env')
load_dotenv(dotenv_path)
# Check the loaded variables
SUPABASE_USER = os.getenv("SUPABASE_USER")
SUPABASE_PASSWORD = os.getenv("SUPABASE_PASSWORD")
SUPABASE_HOST = os.getenv("SUPABASE_HOST")
SUPABASE_PORT = os.getenv("SUPABASE_PORT")
SUPABASE_DATABASE = os.getenv("SUPABASE_DATABASE")

# Check if environment variables are loaded correctly
st.write(f"SUPABASE_USER: {SUPABASE_USER}")
st.write(f"SUPABASE_PASSWORD: {SUPABASE_PASSWORD}")
st.write(f"SUPABASE_HOST: {SUPABASE_HOST}")
st.write(f"SUPABASE_PORT: {SUPABASE_PORT}")
st.write(f"SUPABASE_DATABASE: {SUPABASE_DATABASE}")
st.write("Current working directory:", os.getcwd())  # Print current directory
st.write("Files in the directory:", os.listdir(os.getcwd())) 

DATABASE_URL = f"postgres://{SUPABASE_USER}:{SUPABASE_PASSWORD}@{SUPABASE_HOST}:{SUPABASE_PORT}/{SUPABASE_DATABASE}"


if DATABASE_URL:
    try:
        # Connect to the database using the DATABASE_URL
        conn = psycopg2.connect(DATABASE_URL)  # SSL mode is required for Supabase
        c = conn.cursor()

        # Create table if it doesn't exist
        c.execute('''
            CREATE TABLE IF NOT EXISTS recipes (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                ingredients TEXT NOT NULL,
                instructions TEXT NOT NULL,
                meal_type TEXT NOT NULL
            );
        ''')
        conn.commit()

        # Streamlit form for adding new recipe
        st.header("Add a New Recipe")
        with st.form("recipe_form"):
            recipe_name = st.text_input("Recipe Name")
            ingredients = st.text_area("Ingredients")
            instructions = st.text_area("Instructions")

            # Meal selection dropdown
            meal_type = st.selectbox("Select Meal Type", ["Breakfast", "Lunch", "Dinner"])

            submit = st.form_submit_button("Add Recipe")

            if submit:
                if recipe_name and ingredients and instructions:
                    try:
                        c.execute("INSERT INTO recipes (name, ingredients, instructions, meal_type) VALUES (%s, %s, %s, %s)",
                                  (recipe_name, ingredients, instructions, meal_type))
                        conn.commit()
                        st.success(f"Recipe '{recipe_name}' added successfully!")
                    except Exception as e:
                        st.error(f"Error adding recipe: {e}")
                else:
                    st.error("Please fill in all fields.")

        # Display stored recipes
        st.header("Stored Recipes")

        # Filter recipes by meal type
        meal_filter = st.selectbox("Filter by Meal Type", ["All", "Breakfast", "Lunch", "Dinner"])

        try:
            if meal_filter == "All":
                c.execute("SELECT id, name, meal_type FROM recipes")
            else:
                c.execute("SELECT id, name, meal_type FROM recipes WHERE meal_type = %s", (meal_filter,))

            recipes = c.fetchall()

            if recipes:
                for recipe_id, recipe_name, meal_type in recipes:
                    if st.button(f"{recipe_name}", key=recipe_id):
                        c.execute("SELECT ingredients, instructions FROM recipes WHERE id = %s", (recipe_id,))
                        recipe = c.fetchone()
                        if recipe:
                            st.subheader(f"{recipe_name} ({meal_type})")
                            ingredients_list = recipe[0].split("\n")
                            instructions_list = recipe[1].split("\n")
                            st.write("### Ingredients:")
                            for ingredient in ingredients_list:
                                st.write(f"- {ingredient}")
                            st.write("### Instructions:")
                            for step in instructions_list:
                                st.write(f"- {step}")
                        else:
                            st.error("Recipe not found.")
            else:
                st.write("No recipes found.")
        except Exception as e:
            st.error(f"Error fetching recipes: {e}")

    except Exception as e:
        st.error(f"Error connecting to the database: {e}")



# Close the connection and cursor
    finally:
        if conn:
            c.close()
            conn.close()

else:
    st.error("DATABASE_URL is not set 1 in environment variables.")
