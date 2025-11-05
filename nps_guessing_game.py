import streamlit as st
import requests
import random
import time
from typing import List, Dict, Optional
import os
import urllib.parse

st.set_page_config(
    page_title="NPS Park Guessing Game",
    page_icon="🏞️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS for mobile responsiveness
st.markdown("""
<style>
    /* Mobile-first responsive design */
    @media (max-width: 768px) {
        /* Main container adjustments */
        .main .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }
        
        /* Title styling for mobile */
        h1 {
            font-size: 1.8rem !important;
            text-align: center;
            margin-bottom: 0.5rem;
        }
        
        /* Description text */
        .description {
            text-align: center;
            font-size: 0.9rem;
            margin-bottom: 1rem;
        }
        
        /* Image container for mobile */
        .stImage > div {
            text-align: center;
        }
        
        .stImage img {
            max-width: 100% !important;
            height: auto !important;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        
        /* Ensure custom metrics layout stays on one line */
        div[style*="flex-wrap: nowrap"] {
            flex-wrap: nowrap !important;
        }
        
        /* Button styling for mobile */
        .stButton > button {
            width: 100% !important;
            margin: 0.25rem 0;
            padding: 0.75rem;
            font-size: 1rem;
            border-radius: 8px;
            border: none;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        
        /* Text input styling */
        .stTextInput > div > div > input {
            font-size: 1rem;
            padding: 0.75rem;
            border-radius: 8px;
            border: 2px solid #e0e0e0;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: #4CAF50;
            box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);
        }
        
        /* Guess history styling */
        .guess-item {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 0.75rem;
            margin: 0.5rem 0;
            border-left: 4px solid #4CAF50;
        }
        
        .guess-item.correct {
            border-left-color: #4CAF50;
            background: #e8f5e8;
        }
        
        .guess-item.incorrect {
            border-left-color: #ff9800;
            background: #fff3e0;
        }
        
        /* Mobile-specific: dark text for better contrast on light backgrounds */
        @media (max-width: 768px) {
            .guess-item {
                color: #1f1f1f !important;
            }
            
            .guess-item strong {
                color: #1f1f1f !important;
            }
            
            .guess-item span {
                color: #1f1f1f !important;
            }
        }
        
        /* Sidebar adjustments for mobile */
        .css-1d391kg {
            padding-top: 1rem;
        }
        
        /* Park info section */
        .park-info {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
        }
        
        .park-info h3 {
            color: white;
            margin-bottom: 0.5rem;
        }
        
        /* Success/error messages */
        .stSuccess, .stError, .stWarning {
            border-radius: 8px;
            padding: 1rem;
            margin: 0.5rem 0;
        }
        
        /* Loading spinner */
        .stSpinner {
            text-align: center;
        }
    }
    
    /* Desktop improvements */
    @media (min-width: 769px) {
        .stImage img {
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        
        .stButton > button {
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
    }
    
    /* General improvements */
    .main-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .game-container {
        background: #f8f9fa;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

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
        
        params = {
            'fields': 'images,addresses',
            'limit': 700  
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
                    'designation': park.get('designation', 'Unknown'),  # Add park designation/type
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

def get_unique_designations(parks: List[Dict]) -> List[str]:
    """
    Extract unique park designations from the parks list.
    Returns a sorted list of unique designations.
    """
    designations = set()
    for park in parks:
        designation = park.get('designation', 'Unknown')
        if designation and designation != 'Unknown':
            designations.add(designation)
    return sorted(list(designations))

def filter_parks_by_designation(parks: List[Dict], selected_designations: List[str]) -> List[Dict]:
    """
    Filter parks based on selected designations.
    If no designations are selected, returns all parks.
    """
    if not selected_designations:
        return parks
    
    filtered = []
    for park in parks:
        if park.get('designation') in selected_designations:
            filtered.append(park)
    return filtered

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

def create_bug_report_url(title: str, description: str, labels: str = "bug") -> str:
    """
    Create a pre-filled git issue URL
    """
    github_repo = "rthurmes/np-worlde" 
    
    issue_body = f"""**Bug Description:**
{description}

**Steps to Reproduce:**
1. 
2. 
3. 

**Expected Behavior:**


**Actual Behavior:**


**Browser/Device Info:**
- Browser: 
- Device: 
- Operating System: 

**Additional Context:**
Add any other context about the problem here.

---
*This issue was created via the in-app bug report feature.*
"""
    
    # URL encode the parameters
    params = {
        'title': title,
        'body': issue_body,
        'labels': labels
    }
    
    # Create the GitHub issue URL
    base_url = f"https://github.com/{github_repo}/issues/new"
    query_string = urllib.parse.urlencode(params)
    return f"{base_url}?{query_string}"

def show_bug_report_form():
    """Display the bug report form in the sidebar."""
    st.sidebar.markdown("---")
    st.sidebar.header("🐛 Report a Bug")
    
    with st.sidebar.expander("Found an issue? Let us know!"):
        # Bug report form
        bug_title = st.text_input(
            "Bug Title",
            placeholder="e.g., Wrong park selected when typing 'Glacier'"
        )
        
        bug_description = st.text_area(
            "Describe the bug",
            placeholder="What happened? What did you expect to happen?",
            height=100
        )
        
        bug_type = st.selectbox(
            "Bug Type",
            ["General Bug", "Matching Issue", "Direction/Distance Wrong", "Image Problem", "Performance Issue"]
        )
        
        if st.button("Create Bug Report", width='stretch'):
            if bug_title and bug_description:
                # Create the GitHub issue URL
                full_title = f"[{bug_type}] {bug_title}"
                issue_url = create_bug_report_url(full_title, bug_description)
                
                # Show success message and link
                st.success("Bug report created! Click the link below to submit it on GitHub:")
                st.markdown(f"[Submit Bug Report on GitHub]({issue_url})")
                
                # Also show the URL in case the link doesn't work
                st.code(issue_url, language=None)
                
            else:
                st.error("Please fill in both the title and description.")

def main():
    # Title and description with mobile-friendly styling
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    st.title("NPS Park Guessing Game")
    st.markdown('<div class="description">', unsafe_allow_html=True)
    st.markdown("**Guess the National Park from its image!** Similar to Worldle, but for nps nerds (c)")
    st.markdown("You have 6 guesses to identify the park. After each guess, you'll get distance and direction clues.")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
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
            all_parks = fetch_parks_data(api_key)
        
        if not all_parks:
            st.error("No park data available. Please check your API key and try again.")
            return
        
        # Get unique designations and create filter
        st.sidebar.header("Park Type Filter")
        unique_designations = get_unique_designations(all_parks)
        
        selected_designations = st.sidebar.multiselect(
            "Select park types to include:",
            options=unique_designations,
            default=[],  # Empty by default - shows all parks
            help="Select one or more park types. Leave empty to include all types."
        )
        
        # Filter parks based on selected designations
        parks = filter_parks_by_designation(all_parks, selected_designations)
        
        if not parks:
            st.warning(f"No parks found matching the selected types: {', '.join(selected_designations)}. Please select different types or clear the selection.")
            return
        
        # Show count of filtered parks
        st.sidebar.info(f"**{len(parks)}** parks available with selected types")
        
        # Add bug report form to sidebar
        show_bug_report_form()
        
        # Select a random park if none is selected, or if park type filter changed
        current_park = st.session_state.game_state.get('current_park')
        
        if not current_park:
            st.session_state.game_state['current_park'] = random.choice(parks)
        elif current_park not in parks:
            # Current park is not in filtered list, select a new one
            st.session_state.game_state['current_park'] = random.choice(parks)
            # Reset guesses since we're switching to a different park
            st.session_state.game_state['guesses'] = []
            st.session_state.game_state['game_over'] = False
        
        current_park = st.session_state.game_state['current_park']
        game_state = st.session_state.game_state
        
        # Image section (no container wrapper for cleaner look)
        st.image(
            current_park['image_url'], 
            caption=f"Guess this National Park!",
            width='stretch'  # Use stretch for responsive sizing
        )
        
        # Metrics section with mobile-friendly layout (all on one line using custom HTML)
        st.markdown(f'''
        <div style="display: flex; justify-content: space-around; align-items: center; margin: 1rem 0; flex-wrap: nowrap;">
            <div style="flex: 1; text-align: center; min-width: 0;">
                <div style="font-size: 0.75rem; color: #888; margin-bottom: 0.25rem;">Score</div>
                <div style="font-size: 1.5rem; font-weight: bold;">{game_state['score']}</div>
            </div>
            <div style="flex: 1; text-align: center; min-width: 0;">
                <div style="font-size: 0.75rem; color: #888; margin-bottom: 0.25rem;">Streak</div>
                <div style="font-size: 1.5rem; font-weight: bold;">{game_state['streak']}</div>
            </div>
            <div style="flex: 1; text-align: center; min-width: 0;">
                <div style="font-size: 0.75rem; color: #888; margin-bottom: 0.25rem;">Games</div>
                <div style="font-size: 1.5rem; font-weight: bold;">{game_state['total_games']}</div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        # New Game button
        if st.button("New Game", width='stretch'):
            reset_game()
            st.rerun()
        
        if not game_state['game_over']:
            st.subheader("Make Your Guess")
            
            # Mobile-friendly input section
            guess = st.text_input(
                "Enter part of the park name:",
                placeholder="e.g., Yellowstone, Grand Canyon, Acadia, Yosemite...",
                key="guess_input",
                help="Type any part of the park name to make your guess!"
            )
            
            # Mobile-friendly button layout
            col1, col2 = st.columns([2, 1])
            
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
        
        # Display guess history with mobile-friendly styling
        if game_state['guesses']:
            st.subheader("Your Guesses")
            
            for i, guess_data in enumerate(game_state['guesses'], 1):
                # Create a styled guess item
                guess_class = "correct" if guess_data['is_correct'] else "incorrect"
                status_icon = "🎯" if guess_data['is_correct'] else "❌"
                
                st.markdown(f'''
                <div class="guess-item {guess_class}">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                        <div style="flex: 1; min-width: 200px;">
                            <strong>{status_icon} {i}. {guess_data['park_name']}</strong>
                        </div>
                        <div style="display: flex; gap: 1rem; align-items: center; flex-wrap: wrap;">
                            <span><strong>{guess_data['distance']:.0f} mi</strong></span>
                            <span style="font-size: 1.2em;">{guess_data['direction']}</span>
                        </div>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
        
        if game_state['game_over']:
            st.subheader("🏞️ About This Park")
            
            # Mobile-friendly park info section
            st.markdown(f'''
            <div class="park-info">
                <h3>{current_park['name']}</h3>
                {f'<p><strong>Location:</strong> {current_park["city"]}, {current_park["state"]}</p>' if current_park['city'] and current_park['state'] else ''}
            </div>
            ''', unsafe_allow_html=True)
            
            if current_park['description']:
                st.markdown(f"**Description:**\n\n{current_park['description']}")
    
    else:
        st.warning("Please enter your NPS API key to start playing!")
        st.info("Get your free API key at: https://developer.nps.gov/get-started.htm")

if __name__ == "__main__":
    main()
