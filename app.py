import pandas as pd
import streamlit as st
import numpy as np
from rich.prompt import Prompt

st.set_option('client.showErrorDetails', False)

st.set_page_config(layout="wide") 
custom_html = """
<div class="banner">
    <img src="https://images.unsplash.com/photo-1498837167922-ddd27525d352?q=80&w=1470&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D" alt="Banner Image">
</div>
<style>
    .banner {
        width: 160%;
        height: 300px;
        overflow: hidden;
    }
    .banner img {
        width: 100%;
        object-fit: cover;
    }
</style>
"""
st.components.v1.html(custom_html)
st.title('Recipe Recommendation Generator')
st.header('Find new recipes to try and reduce your food waste!')
st.write('This generator will ask you to input an ingredient you would like a recipe for.')
st.markdown('You can input up to **3 ingredients** if desired when prompted to do so.')

recipe_df = pd.read_csv('recipe_df_app.csv')

list_requested_conditions = []

dietary_input = st.radio('Select your dietary preference:', ['None','Vegetarian','Vegan'])
if dietary_input != None :
    list_requested_conditions.append(str(dietary_input.lower()))

first_ingredient = st.text_input('1. Input the first ingredient: ')
if first_ingredient != None:
    list_requested_conditions.append(first_ingredient.lower())

prompt_second_ingredient = st.radio('Would you like to input a second ingredient?', ['No','Yes'])
if prompt_second_ingredient == 'Yes':
    second_ingredient = st.text_input('2. Input the second ingredient: ')
    if second_ingredient !=None:
        list_requested_conditions.append(second_ingredient.lower())
    prompt_third_ingredient = st.radio('Would you like to input a third ingredient?', ['No','Yes'])
    if prompt_third_ingredient == 'Yes':
        third_ingredient = st.text_input('3. Input the third ingredient: ')
        if third_ingredient != None:
            list_requested_conditions.append(third_ingredient.lower())
    
st.write(f'You have inputed that you would like a recipe with the following: **{list_requested_conditions[1:]}**')

ingredient_columns = recipe_df.columns[9:] 
ingredient_matches = []

# find columns that have ingredient in them and them to list
for each_ingredient in list_requested_conditions:
    matching_columns = [col for col in ingredient_columns if each_ingredient in col.lower()]
    ingredient_matches.append(matching_columns)

# apply a filter where we start by saying all rows are true
condition = pd.Series([True] * len(recipe_df))  # Start with a condition where all rows are True

# for each ingredient check if within the columns it says are for chicken that it has a 1 in the row 
for matching_columns in ingredient_matches:
    if matching_columns:
        ingredient_condition = recipe_df[matching_columns].sum(axis=1) > 0
        condition &= ingredient_condition  # Only keep rows where the condition holds for all ingredients

# Apply the filter based on the final condition
#ingredient_matches = [item for sublist in ingredient_matches for item in sublist]

cols_for_table = ['name','minutes','rating','n_reviews','ingredients','description','vegetarian','vegan','cluster']
filtered_recipes = recipe_df[condition]
filtered_recipes = filtered_recipes[cols_for_table].sort_values('rating',ascending=False)
filtered_recipes = filtered_recipes.rename(columns = {'name': 'Recipe Name','minutes': 'Cook Time (minutes)','rating': 'Rating','n_reviews': 'Number of Reviews','ingredients': 'Ingredient List','description': 'Recipe Description by Author','vegetarian':'Vegetarian','vegan':'Vegan','cluster':'Cluster'})

recipe_of_choice = filtered_recipes.head(3)


if filtered_recipes.shape[0] ==1478:
    st.write('Sorry, there are no recipes meeting your requirements. Please edit your selection.')
    st.stop()

if filtered_recipes.shape[0] != 0:
    st.write(f'We found **{filtered_recipes.shape[0]}** recipes containing these ingredients.')
    
    st.write(f'The recipe with the highest rating is **{recipe_of_choice['Recipe Name'].iloc[0]}**')
    st.header('Recipes matching your prefrences:')
    st.dataframe(recipe_of_choice)
    st.write('Follow this link and search the recipe you would like to try: https://www.food.com/recipe/ ')
    selecting_preferred_recipe = st.radio('Out of the recipes provided, which is your **favouite?**',['1','2','3'])
    
    if selecting_preferred_recipe== '1':
        if filtered_recipes.shape[0] >5:
            cluster_selection = int(recipe_of_choice['Cluster'].iloc[0])
            recipes_in_cluster = filtered_recipes[filtered_recipes['Cluster']== cluster_selection]
            recommendation_recipes = recipes_in_cluster.sample(n=3)
        else:
            cluster_selection = int(recipe_of_choice['Cluster'].iloc[0])
            recipes_in_cluster = recipe_df[recipe_df['cluster']== cluster_selection]
            recommendation_recipes = recipes_in_cluster.sample(n=3)
            recommendation_recipes = recommendation_recipes[cols_for_table].sort_values('rating',ascending=False)
        
    elif selecting_preferred_recipe== '2':
        try:
            if filtered_recipes.shape[0]>5:
                cluster_selection = int(recipe_of_choice['Cluster'].iloc[1])
                recipes_in_cluster = filtered_recipes[filtered_recipes['Cluster']== cluster_selection]
                recommendation_recipes = recipes_in_cluster.sample(n=3)
            else:
                cluster_selection = int(recipe_of_choice['Cluster'].iloc[1])
                recipes_in_cluster = recipe_df[recipe_df['cluster']== cluster_selection]
                recommendation_recipes = recipes_in_cluster.sample(n=3)
                recommendation_recipes = recommendation_recipes[cols_for_table].sort_values('rating',ascending=False)
        except Exception as e :
            st.error('Sorry we could not find recipes to recommend you. Please alter your selection.')
            st.stop()
        
    elif selecting_preferred_recipe== '3':
        try:
            if filtered_recipes.shape[0]>5:
                cluster_selection = int(recipe_of_choice['Cluster'].iloc[2])
                recipes_in_cluster = filtered_recipes[filtered_recipes['Cluster']== cluster_selection]
                recommendation_recipes = recipes_in_cluster.sample(n=3)     
            else:
                cluster_selection = int(recipe_of_choice['Cluster'].iloc[2])
                recipes_in_cluster = recipe_df[recipe_df['cluster']== cluster_selection]
                recommendation_recipes = recipes_in_cluster.sample(n=3)
                recommendation_recipes = recommendation_recipes[cols_for_table].sort_values('rating',ascending=False)
        except Exception as e:
            st.error('Sorry we could not find recipes to recommend you. Please alter your selection.')
            st.stop()
          
    recommendation_recipes = recommendation_recipes.rename(columns = {'name': 'Recipe Name','minutes': 'Cook Time (minutes)','rating': 'Rating','n_reviews': 'Number of Reviews','ingredients': 'Ingredient List','description': 'Recipe Description by Author', 'cluster':'Cluster'})
    
    st.header('Similar Recipes You Might Like:')
    st.write('Here are 3 extra recipes that dont necessarily contain your requested ingredient but are similar to this one that you could try, say tomorrow! ')
    st.dataframe(recommendation_recipes)
    st.subheader('**Enjoy!** ')

if filtered_recipes.shape[0] == 0:
    st.write(' There are recipes in the dataset containing these items, just **not** in the combination you requested: ')
    st.write(f'{ingredient_matches[1:]}')
    st.write('**Please edit your selection and try again.**')
    st.write()
    st.write('These recipes are from the food.com website and the data was sourced at https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions ') 









