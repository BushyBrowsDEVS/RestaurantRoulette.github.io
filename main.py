import json
import random
from flask import Flask, jsonify, render_template, request

#the function to create list of restaurants from with randomizer will pick:
def remove_restaurant(filter_flags, filter_keys, quality, restaurantRandomList):
    with open('restaurantlist.json', 'r') as file:
        food_places = json.load(file)

    name_to_restaurant = {r['name']: r for r in food_places['restaurantList']}

    if not any(filter_flags):
        print(f"No filters selected for {quality}, skipping this filter")
        return

    for restaurant_name in restaurantRandomList[:]:
        restaurant = name_to_restaurant.get(restaurant_name)
        if not restaurant:
            continue

        keep = False
        for flag, key in zip(filter_flags, filter_keys):
            if flag and key in restaurant.get(quality, []):
                keep = True
                break

        if not keep:
            print(f"Removing {restaurant_name} due to {quality} filter")
            restaurantRandomList.remove(restaurant_name)


fastfood = False
dinein = False
fastcasual = False
breakfast = False
lunch = False
dinner = False
american = False
mexican = False
italian = False
asian = False
indian = False
thai = False
mediterranean = False
dessert = False
vegan = False
vegetarian = False
keto = False
glutenfree = False
distance_filter = 8.0

# Create a flask app
app = Flask(
  __name__,
  template_folder='templates',
  static_folder='static'
)

# Index page (now using the index.html file)
@app.route('/')
def index():
  return render_template('index.html')

@app.route('/checkbox-update', methods=['POST'])
def checkbox_update():
    name = request.form.get('name')
    checked = request.form.get('checked') == 'true'

    if name in globals():
        globals()[name] = checked
        print(f"✅ {name} set to {checked}")

    return '', 204


@app.route('/picked-restaurant', methods=['GET'])
def get_picked_restaurant():
    global distance_filter  # Access current distance filter

    with open('restaurantlist.json', 'r') as file:
        food_places = json.load(file)

    restaurant_sublist = [r["name"] for r in food_places["restaurantList"]]

    # Ensure these global variables are defined elsewhere in your app.py, e.g.:
    # fastfood = True
    # dinein = True
    # fastcasual = True
    # breakfast = True
    # lunch = True
    # dinner = True
    # american = True
    # mexican = True
    # italian = True
    # asian = True
    # indian = True
    # mediterranean = True
    # dessert = True
    # vegan = True
    # vegetarian = True
    # keto = True
    # glutenfree = True
    # distance_filter = 100 # Example initial value

    type_food = [fastfood, dinein, fastcasual]
    type_meals = [breakfast, lunch, dinner]
    type_cuisine = [american, mexican, italian, asian, indian, thai, mediterranean]
    dietary_list = [dessert, vegan, vegetarian, keto, glutenfree]

    # You also need to define your remove_restaurant function. Example:
    # def remove_restaurant(filter_booleans, filter_keys, json_field, current_restaurant_names_list):
    #     global food_places # Need access to the full restaurant data
    #     restaurants_to_remove_names = set()
    #     
    #     for i, boolean_filter_value in enumerate(filter_booleans):
    #         if not boolean_filter_value: # If the filter is OFF (e.g., fastfood = False)
    #             for restaurant_data in food_places["restaurantList"]:
    #                 if filter_keys[i] in restaurant_data[json_field]:
    #                     restaurants_to_remove_names.add(restaurant_data['name'])
    #     
    #     # Remove from the list in reverse to avoid index issues
    #     for restaurant_name in sorted(list(restaurants_to_remove_names), reverse=True):
    #         if restaurant_name in current_restaurant_names_list:
    #             current_restaurant_names_list.remove(restaurant_name)


    # Apply existing filters
    remove_restaurant(type_food,
                      ["fastfood", "dinein", "fastcasual"],
                      "type",
                      restaurant_sublist)
    remove_restaurant(
        type_meals,
        ["breakfast", "lunch", "dinner"],
        "meals",
        restaurant_sublist)
    remove_restaurant(
        type_cuisine,
        ["american", "mexican", "italian", "asian", "indian", "mediterranean"],
        "cuisine",
        restaurant_sublist)
    remove_restaurant(
        dietary_list,
        ["dessert", "vegan", "vegetarian", "keto", "glutenfree"],
        "dietary",
        restaurant_sublist
    )

    # Distance filter: remove restaurants farther than distance_filter
    name_to_restaurant = {r['name']: r for r in food_places['restaurantList']}
    # Iterate over a copy of the list to allow modification during iteration
    for restaurant_name in restaurant_sublist[:]: 
        restaurant = name_to_restaurant.get(restaurant_name)
        if restaurant:
            if 'distance' in restaurant:
                if restaurant['distance'] > distance_filter:
                    print(f"Removing {restaurant_name} due to distance filter > {distance_filter} mi")
                    restaurant_sublist.remove(restaurant_name)
            else:
                # If no distance info, you can decide to keep or remove
                print(f"No distance info for {restaurant_name}, removing by default")
                if restaurant_name in restaurant_sublist: # Check if still present before removing
                    restaurant_sublist.remove(restaurant_name)

    # Pick random from filtered list
    if restaurant_sublist:
        restaurant_picked_name = random.choice(restaurant_sublist)
        restaurant_obj = name_to_restaurant[restaurant_picked_name]
        print(f"Randomly picked restaurant: {restaurant_picked_name}")
        return jsonify({
            "restaurant": restaurant_picked_name,
            "image_url": restaurant_obj.get("image", "") # *** CHANGED FROM "image_url" TO "image" ***
        })
    else:
        return jsonify({
            "restaurant": "No restaurants match your filters",
            "image_url": ""
        })


    
@app.route('/distance-update', methods=['POST'])
def distance_update():
    global distance_filter
    distance_str = request.form.get('distance')

    if distance_str is None or distance_str == '':
        print("No distance value was received.")
        return "Error: No distance provided."

    try:
        miles = float(distance_str)
        print(f"Received distance input: {miles} miles")
    except ValueError:
        print(f"Invalid input for distance: {distance_str}")
        return "Error: Please enter a valid number."

    if 0 <= miles <= 8:
        distance_filter = miles
        return f"Searching within {miles} miles..."
    else:
        return "Error: Distance must be between 0 and 8."
  
if __name__ == '__main__':
  # Run the Flask app
  app.run(
  host='0.0.0.0',
  debug=True,
  port=8080
  )



