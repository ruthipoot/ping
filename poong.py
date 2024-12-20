import turtle
import random
import numpy as np
import os

# Create screen
sc = turtle.Screen()
sc.title("Pong game")
sc.bgcolor("black")
sc.setup(width=1000, height=600)

# Left paddle
bot_pad = turtle.Turtle()
bot_pad.speed(0)
bot_pad.shape("square")
bot_pad.color("white")
bot_pad.shapesize(stretch_wid=5, stretch_len=1)
bot_pad.penup()
bot_pad.goto(-400, 0)

# Right paddle (AI)
right_pad = turtle.Turtle()
right_pad.speed(0)
right_pad.shape("square")
right_pad.color("white")
right_pad.shapesize(stretch_wid=5, stretch_len=1)
right_pad.penup()
right_pad.goto(400, 0)

# Ball of circle shape
hit_ball = turtle.Turtle()
hit_ball.speed(10)  # Adjusted speed
hit_ball.shape("circle")
hit_ball.color("blue")
hit_ball.penup()
hit_ball.goto(0, 0)
hit_ball.dx = 9
hit_ball.dy = -9

# Initialize the score
left_player = 0
right_player = 0

# Displays the score
sketch = turtle.Turtle()
sketch.speed(0)
sketch.color("blue")
sketch.penup()
sketch.hideturtle()
sketch.goto(0, 260)
sketch.write("Left_player : 0    Right_player: 0",
             align="center", font=("Courier", 24, "normal"))

# Functions to move paddles

def paddlebup():
    y = right_pad.ycor()
    if y < 250:  # Limit paddle movement
        y += 20
        right_pad.sety(y)

def paddlebdown():
    y = right_pad.ycor()
    if y > -240:  # Limit paddle movement
        y -= 20
        right_pad.sety(y)

def ai_paddle_movement(difficulty="normal"):
    ball_y = hit_ball.ycor()
    paddle_y = bot_pad.ycor()
    
    speed = {"easy": 10, "normal": 20, "hard": 30}.get(difficulty, 20)  # Use different speeds based on difficulty
    
    if ball_y > paddle_y + 10:
        bot_pad.sety(paddle_y + speed)
    elif ball_y < paddle_y - 10:
        bot_pad.sety(paddle_y - speed)
    
    # Add predictive movement based on ball speed for higher difficulty
    if difficulty == "hard" and abs(hit_ball.dy) > 7:
        bot_pad.sety(paddle_y + (ball_y - paddle_y) * 0.5)



# Keyboard bindings
sc.listen()
sc.onkeypress(paddlebup, "Up")
sc.onkeypress(paddlebdown, "Down")
EPISODES = 1000
LEARNING_RATE = 0.1
DISCOUNT_FACTOR = 0.9


class QTable:
    def __init__(self):
        self.table = {}
        self.fileName = 'file.npy'

    def choose_action (self, state, epsilon):
        if state not in self.table:
            self.table[state] = [0, 0]
        if random.random() < epsilon:
            return random.randint(0, 1)  # Explore
        return np.argmax(self.table[state])  # Exploit
 
    def update_q_table(self, state, action, reward, next_state):
        """Update the Q-table using Q-learning."""
        if state not in self.table:
            self.table[state] = [0, 0]
 
        if next_state not in self.table:
            self.table[next_state] = [0, 0]
 
        target = reward

        self.table[state][action] += LEARNING_RATE * (target - self.table[state][action])
 
    def save_q_table(self): 
        """Save the Q-table to a file."""
        np.save(self.fileName, self.table)
        print("Q-table saved to file.")
 
    def load_q_table(self):
        """Load the Q-table from a file."""
        if os.path.exists(self.fileName):
            self.table = np.load(self.fileName, allow_pickle=True).item()
            print("Q-table loaded from file.")
        else:
            print("No Q-table file found. Starting from scratch.")


pong_agent = QTable()
print(QTable)
    
def get_game_State():
    return (bot_pad.ycor(), right_pad.ycor(), hit_ball.xcor(), hit_ball.ycor(), hit_ball.dx, hit_ball.dy)

def game_step():
    global left_player, right_player 
    reward = 0
    # Checking borders
    if hit_ball.ycor() > 280:
        hit_ball.sety(280)
        hit_ball.dy *= -1
        hit_ball.dx += random.uniform(-1, 1)

    if hit_ball.ycor() < -280:
        hit_ball.sety(-280)
        hit_ball.dy *= -1
        hit_ball.dx += random.uniform(-1, 1)

    if hit_ball.xcor() > 500:
        hit_ball.goto(0, 0)
        hit_ball.dy *= -1
        left_player += 1
        reward = -100

    if hit_ball.xcor() < -500:
        hit_ball.goto(0, 0)
        hit_ball.dy *= -1
        right_player += 1
        reward = 100

    # Paddle ball collision
    if (hit_ball.xcor() > 360 and hit_ball.xcor() < 370) and \
            (hit_ball.ycor() < right_pad.ycor() + 50 and hit_ball.ycor() > right_pad.ycor() - 50):
        hit_ball.setx(360)
        hit_ball.dx *= -1
        hit_ball.dy += random.uniform(-1, 1)
        #right collision
        reward = 10


    if (hit_ball.xcor() < -360 and hit_ball.xcor() > -370) and \
            (hit_ball.ycor() < bot_pad.ycor() + 50 and hit_ball.ycor() > right_pad.ycor() - 50):
        hit_ball.setx(-360)
        hit_ball.dx *= -1
        hit_ball.dy += random.uniform(-1, 1)
        #bot collision
    return reward

EPSILON = 0.1
def train_ai():
    game_state = get_game_State()

    for episode in range(EPISODES):
        pong_agent_action = pong_agent.choose_action(game_state, EPSILON)

        if pong_agent_action == 0:
            ai_paddle_movement()
        if pong_agent_action == 1:
            ai_paddle_movement()

        pong_agent_reward = game_step()

        next_state = get_game_State()

        pong_agent.update_q_table(game_state, pong_agent_action, pong_agent_reward, next_state)

        game_state = next_state
train_ai()

# Main game loop
while True:
    sc.update()
    ai_paddle_movement()
    game_state = get_game_State()
    pong_agent_action = pong_agent.choose_action(game_state, 0)
    print(right_pad.ycor())

    if pong_agent_action == 0:
        ai_paddle_movement()
    if pong_agent_action == 1:
        ai_paddle_movement()

    # Add delay to make game smoother

    hit_ball.setx(hit_ball.xcor() + hit_ball.dx)
    hit_ball.sety(hit_ball.ycor() + hit_ball.dy)

    # Checking borders
    if hit_ball.ycor() > 280:
        hit_ball.sety(280)
        hit_ball.dy *= -1

    if hit_ball.ycor() < -280:
        hit_ball.sety(-280)
        hit_ball.dy *= -1

    if hit_ball.xcor() > 500:
        hit_ball.goto(0, 0)
        hit_ball.dy *= -1
        left_player += 1
        sketch.clear()
        sketch.write("Left_player : {}    Right_player: {}".format(
            left_player, right_player), align="center",
            font=("Courier", 24, "normal"))

    if hit_ball.xcor() < -500:
        hit_ball.goto(0, 0)
        hit_ball.dy *= -1
        right_player += 1
        sketch.clear()
        sketch.write("Left_player : {}    Right_player: {}".format(
            left_player, right_player), align="center",
            font=("Courier", 24, "normal"))

    # Paddle ball collision
    if (hit_ball.xcor() > 360 and hit_ball.xcor() < 370) and \
            (hit_ball.ycor() < right_pad.ycor() + 50 and hit_ball.ycor()):
        hit_ball.setx(360)
        hit_ball.dx *= -1
        #right collision

    if (hit_ball.xcor() < -360 and hit_ball.xcor() > -370) and \
            (hit_ball.ycor() < bot_pad.ycor() + 50 and hit_ball.ycor()):
        hit_ball.setx(-360)
        hit_ball.dx *= -1
        #bot collision
    
