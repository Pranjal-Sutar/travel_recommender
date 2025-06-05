import streamlit as st
import pandas as pd
import urllib.parse
import json
import os
st.set_page_config(page_title="Incredible Indian Travel Recommender", page_icon="🕌", layout="wide")
from chatbot import run_chatbot

# Load dataset
df = pd.read_excel("Top Indian Places to Visit.xlsx")

# JSON file to persist user day plans
DATA_FILE = "user_data.json"

def load_user_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_user_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def get_user_plan(email):
    data = load_user_data()
    user_data = data.get(email, {})
    # Handle legacy format (if user_data is a list, convert to new format)
    if isinstance(user_data, list):
        # Group existing places by state
        new_format = {}
        for place_name in user_data:
            place_rows = df[df["Name"] == place_name]
            if not place_rows.empty:
                state = place_rows.iloc[0]["State"]
                if state not in new_format:
                    new_format[state] = []
                new_format[state].append(place_name)
        return new_format
    return user_data

def update_user_plan(email, plans):
    data = load_user_data()
    data[email] = plans
    save_user_data(data)

# Session State Initialization
if "sidebar_collapsed" not in st.session_state:
    st.session_state.sidebar_collapsed = False
if "selected_image" not in st.session_state:
    st.session_state.selected_image = None
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""

# Convert existing day_plan to day_plans if needed
if "day_plan" in st.session_state and "day_plans" not in st.session_state:
    # Convert old format to new format
    day_plans = {}
    for place_name in st.session_state.day_plan:
        place_rows = df[df["Name"] == place_name]
        if not place_rows.empty:
            state = place_rows.iloc[0]["State"]
            if state not in day_plans:
                day_plans[state] = []
            day_plans[state].append(place_name)
    st.session_state.day_plans = day_plans
    # Keep day_plan for backward compatibility
    st.session_state.day_plan = []
elif "day_plans" not in st.session_state:
    st.session_state.day_plans = {}
    
# Make sure day_plans is always a dictionary
if not isinstance(st.session_state.day_plans, dict):
    st.session_state.day_plans = {}

# Filter state preservation
if "selected_state" not in st.session_state:
    st.session_state.selected_state = None
if "selected_city" not in st.session_state:
    st.session_state.selected_city = "All"
if "selected_type" not in st.session_state:
    st.session_state.selected_type = "All"
if "selected_time" not in st.session_state:
    st.session_state.selected_time = "Any"

# Sign-in System
with st.sidebar:
    if not st.session_state.logged_in:
        st.markdown("### 🔐 Sign In")
        email = st.text_input("Email:")
        if st.button("Sign In"):
            if email:
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.session_state.day_plans = get_user_plan(email)
                st.success(f"Signed in as {email}")
            else:
                st.error("Please enter a valid email.")
    else:
        st.markdown(f"👤 Signed in as **{st.session_state.user_email}**")
        if st.button("Sign Out"):
            st.session_state.logged_in = False
            st.session_state.user_email = ""
            st.session_state.day_plans = {}

# Sidebar Day Plan
if not st.session_state.sidebar_collapsed:
    with st.sidebar:
        st.title("Day Plans")

        if st.session_state.day_plans and isinstance(st.session_state.day_plans, dict) and len(st.session_state.day_plans) > 0:
            # Show each state's plan separately
            for state, places in st.session_state.day_plans.items():
                if places:  # Only show states with places
                    st.markdown(f"## 📍 {state}")
                    
                    start_hour = 9
                    total_places = len(places)
                    total_hours = total_places * 3

                    st.markdown(f"**📊 Summary:**")
                    st.markdown(f"- Total Places: `{total_places}`")
                    st.markdown(f"- Total Duration: `{total_hours} hrs`")

                    cities = df[df["Name"].isin(places)]["City"].unique()
                    st.markdown(f"- Cities Covered: `{', '.join(cities)}`")

                    for i, place in enumerate(places):
                        hour = start_hour + i * 3
                        time_str = f"{hour}:00 AM" if hour < 12 else f"{hour-12 if hour > 12 else 12}:00 PM"
                        maps_query = urllib.parse.quote_plus(place)
                        maps_link = f"https://www.google.com/maps/search/?api=1&query={maps_query}"

                        # Food link for the place
                        row = df[df["Name"] == place].iloc[0]
                        food_query = urllib.parse.quote_plus(f"famous or affordable food near {row['Name']} {row['City']} {row['State']}")
                        food_link = f"https://www.google.com/maps/search/{food_query}"

                        st.markdown(f"**🕒 {time_str} – [{place}]({maps_link})**")
                        st.markdown(f"🍽️ [Food Nearby]({food_link})")

                    if st.button(f"❌ Clear Plan for {state}", key=f"clear_{state}"):
                        st.session_state.day_plans.pop(state, None)
                        update_user_plan(st.session_state.user_email, st.session_state.day_plans)
                        st.rerun()
                    
                    st.markdown("---")  # Add separator between state plans
            
            if st.button("❌ Clear All Plans"):
                st.session_state.day_plans = {}
                update_user_plan(st.session_state.user_email, {})
                st.rerun()
        else:
            st.info("No places added yet. Sign in and start planning your day!")

        run_chatbot()

# Main Content
if st.session_state.selected_image:
    # When an image is selected, show it in full screen with a close button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Container to center and limit the size of the image
        st.markdown("""
        <style>
        .image-container {
            display: flex;
            justify-content: center;
            margin: 20px auto;
            max-width: 600px;
        }
        .image-container img {
            max-width: 100%;
            max-height: 500px;
            object-fit: contain;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="image-container">
            <img src="{st.session_state.selected_image}" alt="Selected place">
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Close Image", key="close_full_image"):
            st.session_state.selected_image = None
            st.rerun()
else:
    # Only show the regular UI when no image is selected
    st.title("Incredible India Travel Place Recommender")

    # State Selection
    states = sorted(df["State"].dropna().unique())
    
    # Use the last selected state if available, otherwise default to the first state
    default_state_index = 0
    if st.session_state.selected_state in states:
        default_state_index = states.index(st.session_state.selected_state)
    
    selected_state = st.selectbox("Select State:", states, index=default_state_index)
    st.session_state.selected_state = selected_state  # Update the state selection

    # City Selection
    filtered_cities = df[df["State"] == selected_state]["City"].dropna().unique()
    cities_list = ["All"] + sorted(filtered_cities)
    
    # Use the last selected city if available, otherwise default to "All"
    default_city_index = 0
    if st.session_state.selected_city in cities_list:
        default_city_index = cities_list.index(st.session_state.selected_city)
    
    selected_city = st.selectbox("Select City:", cities_list, index=default_city_index)
    st.session_state.selected_city = selected_city  # Update the city selection

    # Place Type
    if selected_city == "All":
        place_types = sorted(df[df["State"] == selected_state]["Type"].dropna().unique())
    else:
        place_types = sorted(df[(df["State"] == selected_state) & (df["City"] == selected_city)]["Type"].dropna().unique())
    
    types_list = ["All"] + place_types
    
    # Use the last selected type if available, otherwise default to "All"
    default_type_index = 0
    if st.session_state.selected_type in types_list:
        default_type_index = types_list.index(st.session_state.selected_type)
    
    selected_type = st.selectbox("Choose Place Type:", types_list, index=default_type_index)
    st.session_state.selected_type = selected_type  # Update the type selection

    # Best Time
    time_options = sorted(df["Best Time to visit"].dropna().unique())
    time_list = ["Any"] + time_options
    
    # Use the last selected time if available, otherwise default to "Any"
    default_time_index = 0
    if st.session_state.selected_time in time_list:
        default_time_index = time_list.index(st.session_state.selected_time)
    
    selected_time = st.selectbox("Preferred Time to Visit (optional):", time_list, index=default_time_index)
    st.session_state.selected_time = selected_time  # Update the time selection

    # Filtering Logic
    filtered_df = df[df["State"] == selected_state]
    if selected_city != "All":
        filtered_df = filtered_df[filtered_df["City"] == selected_city]
    if selected_type != "All":
        filtered_df = filtered_df[filtered_df["Type"] == selected_type]
    if selected_time != "Any":
        filtered_df = filtered_df[filtered_df["Best Time to visit"] == selected_time]

    # Show Place Cards
    def show_place_card(idx, row):
        maps_query = urllib.parse.quote_plus(f"{row['Name']} {row['City']} {row['State']}")
        maps_link = f"https://www.google.com/maps/dir/?api=1&destination={maps_query}"

        food_query = urllib.parse.quote_plus(f"famous or affordable food near {row['Name']} {row['City']} {row['State']}")
        food_link = f"https://www.google.com/maps/search/{food_query}"

        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown("<div style='padding-top: 70px;'>", unsafe_allow_html=True)
            st.image(row["Image URL"], width=200, use_container_width=False)
            st.markdown("</div>", unsafe_allow_html=True)
            if st.button(f"View Full Image", key=f"img_{idx}"):
                st.session_state.selected_image = row["Image URL"]
                st.rerun()
        with col2:
            st.markdown(f"""
            ### {row['Name']} 📍[Directions]({maps_link})  
            - **Location:** {row['City']}, {row['State']}  
            - **Type:** {row['Type']}  
            - **Rating:** ⭐ {row['Google review rating']}  
            - **Best Time to Visit:** {row['Best Time to visit']}  
            - [Famous/Affordable Food Nearby]({food_link})  
            """)
            if st.button(f"➕ Add to Day Plan", key=f"add_{idx}"):
                if not st.session_state.logged_in:
                    st.warning("Please sign in to add places to your day plan.")
                else:
                    # Get the state for this place
                    place_state = row['State']
                    
                    # Initialize the state in the dictionary if not exists
                    if place_state not in st.session_state.day_plans:
                        st.session_state.day_plans[place_state] = []
                        
                    # Add the place to the appropriate state's plan if not already there
                    if row['Name'] not in st.session_state.day_plans[place_state]:
                        st.session_state.day_plans[place_state].append(row['Name'])
                        update_user_plan(st.session_state.user_email, st.session_state.day_plans)

    # Show Results
    if not filtered_df.empty:
        city_display = selected_city if selected_city != "All" else selected_state
        st.subheader(f"🎯 Recommended Places in {city_display} ({selected_type})")
        for idx, row in filtered_df.iterrows():
            show_place_card(idx, row)
    else:
        st.warning("No places found for your selected filters.")
        st.subheader("🌍 Other Places in the State:")
        fallback_df = df[df["State"] == selected_state]
        for idx, row in fallback_df.iterrows():
            show_place_card(f"fallback_{idx}", row)
