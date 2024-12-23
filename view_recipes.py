import streamlit as st
import psycopg2
from home import SUPABASE_USER, SUPABASE_PASSWORD, SUPABASE_HOST, SUPABASE_PORT, SUPABASE_DATABASE

# Database connection (use your existing connection logic)
DATABASE_URL = f"postgres://{SUPABASE_USER}:{SUPABASE_PASSWORD}@{SUPABASE_HOST}:{SUPABASE_PORT}/{SUPABASE_DATABASE}"


st.title("View Recipes")

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
                    if st.button(f"{recipe_name}", key=recipe_id):
                        c.execute("SELECT ingredients, instructions FROM recipes WHERE id = %s", (recipe_id,))
                        recipe = c.fetchone()
                        if recipe:
                            st.subheader(f"{recipe_name} ({meal_type})")
                            st.write("### Ingredients:")
                            st.write(recipe[0])
                            st.write("### Instructions:")
                            st.write(recipe[1])
            else:
                st.write("No recipes found.")
except Exception as e:
    st.error(f"Error fetching recipes: {e}")
