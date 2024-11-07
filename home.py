# home.py
import streamlit as st
import sqlite3

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('recipes.db')
c = conn.cursor()

# Create a table if it doesn't already exist
c.execute('''CREATE TABLE IF NOT EXISTS recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                ingredients TEXT NOT NULL,
                instructions TEXT NOT NULL
            )''')
conn.commit()

# Streamlit app
st.title("Recipe Storage App")

# Input form to add a new recipe
st.header("Add a New Recipe")
with st.form("recipe_form"):
    recipe_name = st.text_input("Recipe Name")
    ingredients = st.text_area("Ingredients")
    instructions = st.text_area("Instructions")
    submit = st.form_submit_button("Add Recipe")

    if submit:
        if recipe_name and ingredients and instructions:
            c.execute("INSERT INTO recipes (name, ingredients, instructions) VALUES (?, ?, ?)",
                      (recipe_name, ingredients, instructions))
            conn.commit()
            st.success(f"Recipe '{recipe_name}' added successfully!")
        else:
            st.error("Please fill in all fields.")

# Display stored recipes
st.header("Stored Recipes")
recipes = c.execute("SELECT id, name FROM recipes").fetchall()

if recipes:
    for recipe_id, recipe_name in recipes:
        if st.button(f"View '{recipe_name}'", key=recipe_id):
            recipe = c.execute("SELECT ingredients, instructions FROM recipes WHERE id = ?", (recipe_id,)).fetchone()
            if recipe:
                st.subheader(recipe_name)
                st.text_area("Ingredients", recipe[0], height=150, disabled=True)
                st.text_area("Instructions", recipe[1], height=300, disabled=True)
else:
    st.write("No recipes found.")

# Close the database connection when done
conn.close()
