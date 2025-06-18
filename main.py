from flask import Flask, request, jsonify, render_template
import random
import json

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

    type_food = [fastfood, dinein, fastcasual]
    type_meals = [breakfast, lunch, dinner]
    type_cuisine = [american, mexican, italian, asian, indian, mediterranean]
    dietary_list = [dessert, vegan, vegetarian, keto, glutenfree]

    # Apply existing filters
    remove_restaurant(type_food, ["fastfood", "dinein", "fastcasual"], "type", restaurant_sublist)
    remove_restaurant(type_meals, ["breakfast", "lunch", "dinner"], "meals", restaurant_sublist)
    remove_restaurant(type_cuisine, ["american", "mexican", "italian", "asian", "indian", "mediterranean"], "cuisine", restaurant_sublist)
    remove_restaurant(dietary_list, ["dessert", "vegan", "vegetarian", "keto", "glutenfree"], "dietary", restaurant_sublist)

    # Distance filter: remove restaurants farther than distance_filter
    name_to_restaurant = {r['name']: r for r in food_places['restaurantList']}
    for restaurant_name in restaurant_sublist[:]:
        restaurant = name_to_restaurant.get(restaurant_name)
        if restaurant:
            # Assume your JSON has a 'distance' field in miles
            if 'distance' in restaurant:
                if restaurant['distance'] > distance_filter:
                    print(f"Removing {restaurant_name} due to distance filter > {distance_filter} mi")
                    restaurant_sublist.remove(restaurant_name)
            else:
                # If no distance info, you can decide to keep or remove
                print(f"No distance info for {restaurant_name}, removing by default")
                restaurant_sublist.remove(restaurant_name)

    # Pick random from filtered list
    if restaurant_sublist:
        restaurant_picked = random.choice(restaurant_sublist)
        print(f"Randomly picked restaurant: {restaurant_picked}")
    else:
        restaurant_picked = "No restaurants match your filters"
        print(restaurant_picked)

    return jsonify({"restaurant": restaurant_picked})
    
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



