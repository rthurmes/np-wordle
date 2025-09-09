import streamlit as st
import requests
import random
import time
from typing import List, Dict, Optional
import os

st.set_page_config(
    page_title="NPS Park Guessing Game",
    page_icon="🏞️",
    layout="wide"
)

NPS_API_BASE = "https://developer.nps.gov/api/v1"
DEFAULT_API_KEY = "DEMO_KEY"  

@st.cache_data(ttl=3600)  
def fetch_parks_data(api_key: str) -> List[Dict]:
    """
    Fetch park data from NPS API with images and location information.
    Returns a list of parks with their images and location data.
    """
    try:
        headers = {'X-Api-Key': api_key}
        
        # Fetch parks with images and addresses
        params = {
            'fields': 'images,addresses',
            'limit': 500  # Get more parks for variety
        }
        
        response = requests.get(f"{NPS_API_BASE}/parks", headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        parks_with_images = []
        
        for park in data.get('data', []):
            # Only include parks that have images and location data
            if (park.get('images') and 
                park.get('addresses') and 
                len(park['images']) > 0 and 
                len(park['addresses']) > 0):
                
                # Get the first image
                image = park['images'][0]
                address = park['addresses'][0]
                
                park_data = {
                    'name': park.get('fullName', 'Unknown Park'),
                    'park_code': park.get('parkCode', ''),
                    'description': park.get('description', ''),
                    'image_url': image.get('url', ''),
                    'image_alt': image.get('altText', ''),
                    'image_caption': image.get('caption', ''),
                    'city': address.get('city', ''),
                    'state': address.get('stateCode', ''),
                    'state_name': address.get('stateName', ''),
                    'coordinates': {
                        'lat': float(park.get('latitude', 0)) if park.get('latitude') else 0,
                        'lon': float(park.get('longitude', 0)) if park.get('longitude') else 0
                    }
                }
                
                # Only add if we have essential data
                if park_data['image_url'] and park_data['state']:
                    parks_with_images.append(park_data)
        
        return parks_with_images
        
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data from NPS API: {e}")
        return []
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return []

def calculate_distance_miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    distance between two coordinates in miles
    """
    import math
    
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 3959
    return c * r

def get_direction_arrow(lat1: float, lon1: float, lat2: float, lon2: float) -> str:
    """
    Get direction arrow from guess to target park.
    Returns an arrow emoji pointing in the general direction.
    """
    import math
    
    # bearing
    dlon = math.radians(lon2 - lon1)
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    
    y = math.sin(dlon) * math.cos(lat2_rad)
    x = math.cos(lat1_rad) * math.sin(lat2_rad) - math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon)
    
    bearing = math.degrees(math.atan2(y, x))
    bearing = (bearing + 360) % 360
    
    
    if 337.5 <= bearing or bearing < 22.5:
        return "⬆️"  
    elif 22.5 <= bearing < 67.5:
        return "↗️"  
    elif 67.5 <= bearing < 112.5:
        return "➡️" 
    elif 112.5 <= bearing < 157.5:
        return "↘️"  
    elif 157.5 <= bearing < 202.5:
        return "⬇️" 
    elif 202.5 <= bearing < 247.5:
        return "↙️" 
    elif 247.5 <= bearing < 292.5:
        return "⬅️" 
    elif 292.5 <= bearing < 337.5:
        return "↖️"  
    else:
        return "⬆️"  

def find_park_by_guess(guess: str, parks: List[Dict]) -> Optional[Dict]:
    """
    Find a park that matches the user's guess.
    Requires at least one full word match in the park name (excluding generic park words).
    Prioritizes exact matches over partial matches.
    """
    guess_lower = guess.lower().strip()
    
    # ignore short bois
    if len(guess_lower) < 2:
        return None
    
    # common generic park words to exclude from matching. come back to this later. probably a better way
    generic_words = {
        'national', 'park', 'monument', 'memorial', 'historic', 'historical', 
        'site', 'area', 'preserve', 'reserve', 'recreation', 'seashore', 
        'lakeshore', 'river', 'trail', 'scenic', 'byway', 'corridor',
        'battlefield', 'cemetery', 'cemeteries', 'military', 'state'
    }
    
    guess_words = guess_lower.split()
    meaningful_guess_words = [word for word in guess_words if word not in generic_words]
    
    if not meaningful_guess_words:
        return None
    
    matching_parks = []
    # this part is ranking based on matching words, so "glacier national park" will get a higher score than "glacier bay national park"
    for park in parks:
        park_name = park['name'].lower()
        
        park_words = park_name.split()
        meaningful_park_words = [word for word in park_words if word not in generic_words]
        
        if not meaningful_park_words:
            continue
        
        matches_found = 0
        exact_matches = 0
        total_guess_words = len(meaningful_guess_words)
        match_score = 0 
        
        for guess_word in meaningful_guess_words:
            word_matched = False
            
            # First try exact word matches
            for park_word in meaningful_park_words:
                if guess_word == park_word:
                    matches_found += 1
                    exact_matches += 1
                    match_score += 100
                    word_matched = True
                    break
            
            if not word_matched:
                for park_word in meaningful_park_words:
                    if len(park_word) >= 3 and guess_word in park_word and len(guess_word) >= 3:
                        matches_found += 1
                        match_ratio = len(guess_word) / len(park_word)
                        match_score += int(50 * match_ratio)
                        word_matched = True
                        break
        
        if matches_found == total_guess_words and total_guess_words > 0:
            name_length_penalty = len(meaningful_park_words) * 5
            final_score = match_score - name_length_penalty
            matching_parks.append((park, exact_matches, final_score))
    
    if matching_parks:
        matching_parks.sort(key=lambda x: (-x[2], -x[1], x[0]['name']))
        return matching_parks[0][0]
    
    return None

def initialize_game_state():
    """Initialize the game state in session state."""
    if 'game_state' not in st.session_state:
        st.session_state.game_state = {
            'current_park': None,
            'guesses': [],
            'max_guesses': 6,
            'game_over': False,
            'score': 0,
            'streak': 0,
            'total_games': 0
        }

def reset_game():
    """Reset the current game while keeping overall stats."""
    st.session_state.game_state.update({
        'current_park': None,
        'guesses': [],
        'game_over': False
    })

def main():
    # Title and description
    st.title("NPS Park Guessing Game")
    st.markdown("**Guess the National Park from its image!** Similar to Worldle, but for nps nerds (c)")
    st.markdown("You have 6 guesses to identify the park. After each guess, you'll get distance and direction clues.")
    
    # API Key input
    st.sidebar.header("API Configuration")
    api_key = st.sidebar.text_input(
        "NPS API Key", 
        value=os.getenv('NPS_API_KEY', DEFAULT_API_KEY),
        help="Get your free API key from https://developer.nps.gov/get-started.htm",
        type="password"
    )
    
    initialize_game_state()
    
    if api_key:
        with st.spinner("Loading National Parks data..."):
            parks = fetch_parks_data(api_key)
        
        if not parks:
            st.error("No park data available. Please check your API key and try again.")
            return
        
        if not st.session_state.game_state['current_park']:
            st.session_state.game_state['current_park'] = random.choice(parks)
        
        current_park = st.session_state.game_state['current_park']
        game_state = st.session_state.game_state
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.image(
                current_park['image_url'], 
                caption=f"Guess this National Park!",
                width='stretch'
            )
        
        with col2:
            st.metric("Score", game_state['score'])
            st.metric("Streak", game_state['streak'])
            st.metric("Total Games", game_state['total_games'])
            
            if st.button("New Game", width='stretch'):
                reset_game()
                st.rerun()
        
        if not game_state['game_over']:
            st.subheader("Make Your Guess")
            
            guess = st.text_input(
                "Enter part of the park name:",
                placeholder="e.g., Yellowstone, Grand Canyon, Acadia, Yosemite...",
                key="guess_input"
            )
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                if st.button("Submit Guess", width='stretch', type="primary"):
                    if guess:
                        guessed_park = find_park_by_guess(guess, parks)
                        
                        if guessed_park:
                            distance = calculate_distance_miles(
                                guessed_park['coordinates']['lat'],
                                guessed_park['coordinates']['lon'],
                                current_park['coordinates']['lat'],
                                current_park['coordinates']['lon']
                            )
                            
                            direction = get_direction_arrow(
                                guessed_park['coordinates']['lat'],
                                guessed_park['coordinates']['lon'],
                                current_park['coordinates']['lat'],
                                current_park['coordinates']['lon']
                            )
                            
                            
                            is_correct = (guessed_park['name'] == current_park['name'])
                            
                            game_state['guesses'].append({
                                'guess': guess,
                                'park_name': guessed_park['name'],
                                'distance': distance,
                                'direction': direction,
                                'is_correct': is_correct
                            })
                            
                            if is_correct:
                                st.success(f"Correct! It's {current_park['name']}!")
                                game_state['score'] += 1
                                game_state['streak'] += 1
                                game_state['game_over'] = True
                                game_state['total_games'] += 1
                            else:
                                st.warning(f"Not quite! You guessed {guessed_park['name']}")
                                if len(game_state['guesses']) >= game_state['max_guesses']:
                                    st.error(f"Game Over! The correct answer was {current_park['name']}")
                                    game_state['streak'] = 0
                                    game_state['game_over'] = True
                                    game_state['total_games'] += 1
                        else:
                            st.error("Park not found. Please try a different guess.")
                    else:
                        st.warning("Please enter a guess!")
            
            with col2:
                if st.button("Give Up", width='stretch'):
                    st.error(f"The correct answer was {current_park['name']}!")
                    game_state['streak'] = 0
                    game_state['game_over'] = True
                    game_state['total_games'] += 1
        
        # Display guess history
        if game_state['guesses']:
            st.subheader("Your Guesses")
            
            for i, guess_data in enumerate(game_state['guesses'], 1):
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                
                with col1:
                    if guess_data['is_correct']:
                        st.success(f"✅ {i}. {guess_data['park_name']}")
                    else:
                        st.info(f"❌ {i}. {guess_data['park_name']}")
                
                with col2:
                    st.write(f"{guess_data['distance']:.0f} mi")
                
                with col3:
                    st.write(guess_data['direction'])
                
                with col4:
                    if guess_data['is_correct']:
                        st.write("🎯")
                    else:
                        st.write("❌")
        
        if game_state['game_over']:
            st.subheader("🏞️ About This Park")
            st.write(f"**{current_park['name']}**")
            if current_park['description']:
                st.write(current_park['description'])
            if current_park['city'] and current_park['state']:
                st.write(f"📍 Located in {current_park['city']}, {current_park['state']}")
    
    else:
        st.warning("Please enter your NPS API key to start playing!")
        st.info("Get your free API key at: https://developer.nps.gov/get-started.htm")

if __name__ == "__main__":
    main()
