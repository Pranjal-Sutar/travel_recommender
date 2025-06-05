import streamlit as st
import markdown

# Sample hardcoded travel data
travel_data = [
    {
        "name": "Goa",
        "best_time": "Winter (November to February)",
        "speciality": "Beaches, Nightlife, Portuguese Heritage",
        "famous_food": "Prawn Balchão, Bebinca"
    },
    {
        "name": "Manali",
        "best_time": "Summer (April to June), Winter (October to February)",
        "speciality": "Snow-capped mountains, Adventure sports, River rafting",
        "famous_food": "Siddu, Trout Fish"
    },
    {
        "name": "Jaipur",
        "best_time": "Winter (November to February)",
        "speciality": "Forts, Palaces, Rajasthani Culture",
        "famous_food": "Dal Baati Churma, Ghewar"
    },
    {
        "name": "Kerala",
        "best_time": "Monsoon (June to September), Winter (October to February)",
        "speciality": "Backwaters, Ayurvedic treatments, Lush greenery",
        "famous_food": "Appam with Stew, Kerala Sadya"
    },
    {
        "name": "Leh Ladakh",
        "best_time": "Summer (May to September)",
        "speciality": "Barren landscapes, Monasteries, High passes",
        "famous_food": "Thukpa, Skyu"
    },
    {
        "name": "Darjeeling",
        "best_time": "Summer (April to June), Autumn (October-November)",
        "speciality": "Tea Gardens, Toy Train, Himalayan Views",
        "famous_food": "Momos, Darjeeling Tea"
    },
    {
        "name": "Andaman Islands",
        "best_time": "Winter (October to May)",
        "speciality": "Snorkeling, Pristine beaches, Marine life",
        "famous_food": "Grilled Lobsters, Coconut Prawn Curry"
    },
]

def generate_response(user_input):
    user_input = user_input.lower()

    if any(word in user_input for word in ["hello", "hi", "hey"]):
        return "👋 Hey traveler! Ask me about any Indian destination, best seasons to visit, or local highlights! 🗺️"

    for place in travel_data:
        if place["name"].lower() in user_input:
            return f"""📍 **{place['name']}**  
🗓️ **Best Time to Visit:** *{place['best_time']}*  
🌟 **Speciality:** *{place['speciality']}*  
🍽️ **Famous Food:** *{place['famous_food']}*"""

    for season in ["summer", "monsoon", "winter"]:
        if season in user_input:
            matches = [p["name"] for p in travel_data if season in p["best_time"].lower()]
            if matches:
                return f"☀️ **Places to visit in {season.title()}**:\n- " + "\n- ".join(matches)

    return "🤖 Hmm, I didn't get that. Try asking me about a place or season like 'Tell me about Goa' or 'Places to visit in summer'."
 # Make sure this is imported at the top

def run_chatbot():
    st.markdown("<h2 style='text-align:center;'>🌍 Indian Travel Chatbot</h2>", unsafe_allow_html=True)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_input = st.chat_input("Where would you like to go or ask about?", key="travel_chat_input")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        response = generate_response(user_input)
        st.session_state.chat_history.append({"role": "assistant", "content": response})

    for msg in st.session_state.chat_history:
        bubble_color = "#d4f5dc" if msg["role"] == "user" else "#e0f0ff"
        align = "flex-end" if msg["role"] == "user" else "flex-start"

        # Render content using markdown with newline to <br>
        html_content = markdown.markdown(msg["content"]).replace("\n", "<br>")

        st.markdown(f"""
        <div style='display:flex; justify-content:{align}; margin-bottom: 6px;'>
            <div style='background-color:{bubble_color}; padding:10px 14px; border-radius:15px; max-width:75%; font-size:15px; line-height:1.3; color:black;'>
                {html_content}
            </div>
        </div>
        """, unsafe_allow_html=True)
