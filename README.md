# FootballTatics-BackEnd

This project is a Django-based backend API for **FootballTatics**, an application designed for football (soccer) managers and enthusiasts. It allows users to manage their teams (elencos), add players with specific attributes, and receive AI-powered recommendations for optimal player positioning and team formations.

## Features

* **User Authentication**: Secure user registration and login using JWT (JSON Web Tokens).
* **Team Management**: Full CRUD (Create, Read, Update, Delete) functionality for managing squads (`Elencos`) and players (`Jogadores`).
* **Player Attributes**: Detailed player profiles including age, height, weight, preferred foot, and skill ratings (velocity, shot, pass, defense).
* **Pre-defined Formations**: A database of standard football formations (e.g., 4-4-2, 4-3-3, 3-5-2) with tactical descriptions.
* **AI-Powered Talent Analysis**: An endpoint (`/api/procurar-talentos/`) that uses a deep learning model to analyze a player's stats and suggest their most suitable field position.
* **AI Tactical Suggestions**: An endpoint (`/api/sugerir-tatica/`) that analyzes the entire squad and recommends the best tactical formations based on the AI's player position analysis.

---

## Artificial Intelligence Model

The core of this application is the AI model that provides tactical insights. It's designed to function as an "AI Assistant Coach," helping users make informed decisions about player roles and team strategy.

### Objective
The primary goal of the AI is twofold:
1.  **Player Position Prediction**: To analyze a player's physical and technical attributes (height, weight, speed, shot, pass, defense) and predict their most effective position on the field (e.g., Center Back, Central Midfielder, Striker).
2.  **Team Formation Suggestion**: Based on the predicted positions for all players in a squad, the AI aggregates this data to recommend the most suitable tactical formation (e.g., 4-3-3, 3-5-2) that maximizes the team's strengths.

### Dataset
The model was trained on the **European Soccer Database** from Kaggle. This comprehensive dataset contains detailed attributes for over 10,000 players from various European leagues, which are found in the `deep_learning_model/data/database.sqlite` file. The model specifically uses the `Player` and `Player_Attributes` tables, which provide both biographical data (height, weight) and in-game statistics updated over several seasons.

### Data Preprocessing & Feature Engineering
The data underwent several transformations to prepare it for training, as detailed in the `deep_learning_model/notebooks/00_formatting_data.ipynb` notebook:

1.  **Data Cleaning**: Handled missing values and removed inconsistent data entries.
2.  **Duplicate Handling**: For players with multiple entries across different seasons, their stats were averaged to create a single, representative profile.
3.  **Feature Engineering**: New, composite features were created to better capture a player's overall abilities:
    * `wh`: A combined metric of weight and height.
    * `finishing_acc`: An average of finishing, heading accuracy, and shot power.
    * `skills`: An average of crossing, dribbling, curve, and ball control.
    * `movement`: An average of acceleration, sprint speed, agility, balance, and stamina.
    * `defensive_rating`: An average of marking, standing tackle, and sliding tackle.
4.  **Target Variable**: The player positions were one-hot encoded to serve as the multi-label target for the classifier.
5.  **Data Balancing**: The dataset was balanced using resampling techniques to prevent the model from being biased toward more common positions.

### Model Architecture & Training
The final model, scripted in `deep_learning_model/train_model.py`, is a neural network built with TensorFlow and Keras.

* **Architecture**: A `Sequential` model consisting of multiple `Dense` layers with `elu` activation, interspersed with `BatchNormalization` and `Dropout` layers to improve training stability and prevent overfitting. The output layer uses a `sigmoid` activation function, making it suitable for multi-label classification where a player can be effective in more than one position.
* **Training**:
    * **Optimizer**: Nadam
    * **Loss Function**: `binary_crossentropy`
    * **Callbacks**: `EarlyStopping` was used to halt training when the validation loss stopped improving, and `ReduceLROnPlateau` was used to adjust the learning rate dynamically.
* **Output**: The script saves the trained model as `modelspi2025_v12.h5` and the data scaler as `scaler_wh.pkl`. These artifacts are loaded by the Django backend to make live predictions.

### Integration with the API
The `api/ia_logic.py` script serves as the bridge between the Django API and the trained AI model.

* The `recomendar_formacao_com_ia` function takes the player data from a user's squad.
* It preprocesses the data using the saved `scaler`, ensuring the input matches the format the model was trained on.
* It feeds the data to the loaded TensorFlow model, which outputs a probability distribution across all possible field positions for each player.
* The position with the highest probability is chosen as the player's "suggested position."
* Finally, a rule-based system (`_sugerir_taticas_por_fit`) counts the number of players in each tactical group (Defenders, Midfielders, Attackers) to determine and suggest the most fitting team formation.

---

## API Endpoints

The API is exposed under the `/api/` prefix.

| Endpoint                 | Method | Description                                                | Authentication |
| ------------------------ | ------ | ---------------------------------------------------------- | -------------- |
| `/api/register/`           | `POST` | Registers a new user and creates an initial empty team.    | Public         |
| `/api/login/`              | `POST` | Obtains a JWT token pair (access and refresh) for a user.  | Public         |
| `/api/login/refresh/`      | `POST` | Refreshes an expired JWT access token.                     | Public         |
| `/api/me/`                 | `GET`    | Retrieves the profile of the currently logged-in user.     | Required       |
| `/api/elencos/`            | `GET`, `POST` | List all squads for the user or create a new one.          | Required       |
| `/api/elencos/<id>/`       | `GET`, `PUT`, `DELETE` | Retrieve, update, or delete a specific squad.            | Required       |
| `/api/jogadores/`          | `GET`, `POST` | List all players for the user or create a new one.         | Required       |
| `/api/jogadores/<id>/`     | `GET`, `PUT`, `DELETE` | Retrieve, update, or delete a specific player.           | Required       |
| `/api/formacoes/`          | `GET`    | Lists all available pre-defined tactical formations.       | Public         |
| `/api/salvar-formacao/`    | `POST` | Saves the user's chosen formation.                         | Required       |
| `/api/formacao-escolhida/` | `GET`    | Retrieves the user's saved formation.                      | Required       |
| `/api/sugerir-tatica/`     | `GET`    | **AI**: Suggests team tactics based on the current squad. | Required       |
| `/api/procurar-talentos/`  | `GET`    | **AI**: Analyzes and suggests the best position for each player. | Required       |

---

## Technologies Used

* **Backend**: Django, Django REST Framework
* **Authentication**: Simple JWT for an stateless API
* **Deep Learning**: TensorFlow (Keras)
* **Data Manipulation**: Pandas, Scikit-learn
* **Database**: SQLite3 (default)
* **API Documentation**: drf-yasg (Swagger UI at `/swagger/`)

---

## Local Setup and Installation

### Prerequisites
* Python 3.10+
* pip

### Installation
1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/FootballTatics-BackEnd.git
    cd FootballTatics-BackEnd
    ```

2.  **Set up a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install backend dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Install deep learning dependencies:**
    *Note: These are in a separate file as they are not needed for all backend operations, but are required for the AI features.*
    ```bash
    pip install -r deep_learning_model/requirements.txt
    ```

5.  **Apply database migrations:**
    ```bash
    python manage.py migrate
    ```

6.  **Load initial formation data (Optional):**
    The project includes a fixture with pre-defined football formations. To load it, run:
    ```bash
    python manage.py loaddata core/fixtures/formacoes.json
    ```

7.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```
    The API will be available at `http://127.0.0.1:8000/`.
    The Swagger UI for API documentation will be at `http://127.0.0.1:8000/swagger/`.
