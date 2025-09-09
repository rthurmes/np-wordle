# 🏞️ NPS Park Guessing Game

A Worldle-inspired guessing game where players identify National Parks from their images! Built with Streamlit and the National Park Service API.

## 🎮 How to Play

1. **Look at the image** - A beautiful photo from a National Park is displayed
2. **Make your guess** - Enter the park name, city, or state
3. **Get clues** - After each guess, you'll receive:
   - Distance from your guess to the correct park (in kilometers)
   - Direction arrow pointing toward the correct location
4. **Win in 6 tries** - Guess the correct park within 6 attempts!

## 🚀 Getting Started

### Prerequisites

- Python 3.7+
- NPS API Key (free from [developer.nps.gov](https://developer.nps.gov/get-started.htm))

### Installation

1. **Clone or download this repository**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Get your NPS API Key:**
   - Visit [NPS Developer Resources](https://developer.nps.gov/get-started.htm)
   - Sign up for a free account
   - Generate your API key

4. **Run the game:**
   ```bash
   streamlit run nps_guessing_game.py
   ```

5. **Enter your API key** in the sidebar when the app loads

## 🎯 Features

- **Daily Challenge**: New random park each game
- **Distance & Direction Clues**: Similar to Worldle's feedback system
- **Score Tracking**: Keep track of your wins and streaks
- **Educational**: Learn about National Parks across the US
- **Responsive Design**: Works on desktop and mobile

## 🏞️ Game Mechanics

### Scoring System
- **Correct Guess**: +1 point, streak continues
- **Wrong Guess**: No points, but you get helpful clues
- **Give Up**: Streak resets to 0

### Clue System
- **Distance**: Shows how far your guess is from the correct park
- **Direction**: Arrow pointing toward the correct location
- **Smart Matching**: Searches by park name, city, or state

## 🔧 Technical Details

### API Integration
- Uses NPS API v1 to fetch park data and images
- Caches data for 1 hour to improve performance
- Handles API errors gracefully

### Technologies
- **Streamlit**: Web app framework
- **Requests**: HTTP library for API calls
- **Haversine Formula**: Distance calculations between coordinates

## 🎨 Customization

You can easily customize the game by modifying:

- **Number of guesses**: Change `max_guesses` in the game state
- **Cache duration**: Modify `ttl` in the `@st.cache_data` decorator
- **API parameters**: Adjust the `params` in `fetch_parks_data()`

## 🐛 Troubleshooting

### Common Issues

1. **"No park data available"**
   - Check your API key is correct
   - Ensure you have internet connection
   - Try refreshing the page

2. **"Park not found"**
   - Try different variations of the park name
   - Use city or state names instead
   - Check spelling

3. **Images not loading**
   - Some parks may not have images
   - Check your internet connection
   - The app will automatically skip parks without images

## 📝 License

This project is for educational purposes. The National Park Service data is public domain.

## 🤝 Contributing

Feel free to submit issues, feature requests, or pull requests to improve the game!

## 🙏 Acknowledgments

- **National Park Service** for providing the amazing API and data
- **Worldle** for the inspiration and game mechanics
- **Streamlit** for the excellent web app framework
