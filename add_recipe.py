import streamlit as st
import psycopg2

# Database connection (use your existing connection logic)
DATABASE_URL = st.secrets["supabase"]["DATABASE_URL"]

def create_table():
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as c:
            c.execute('''CREATE TABLE IF NOT EXISTS recipes (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                ingredients TEXT NOT NULL,
                instructions TEXT NOT NULL,
                meal_type TEXT NOT NULL
            );''')
            conn.commit()

st.title("Add a New Recipe")

create_table()

with st.form("recipe_form"):
    recipe_name = st.text_input("Recipe Name")
    ingredients = st.text_area("Ingredients")
    instructions = st.text_area("Instructions")
    meal_type = st.selectbox("Select Meal Type", ["Breakfast", "Lunch", "Dinner", "Dessert"])
    submit = st.form_submit_button("Add Recipe")

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
        except Exception as e:
            st.error(f"Error adding recipe: {e}")
    else:
        st.error("Please fill in all fields.")
