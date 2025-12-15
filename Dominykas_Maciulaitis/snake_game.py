# Dominykas Mačiulaitis

import turtle
import time
import random
import math
import pickle
import os

delay = 0.001 # Speed up for training
Q_TABLE_FILE = "q_table.pkl"
LOG_FILE = "training_log.txt"

# Score
score = 0
high_score = 0
episode_reward = 0
max_episode_reward = -1000
generation = 1
paused = False

# Set up the screen
wn = turtle.Screen()
wn.title("Snake Game")
wn.bgcolor("green")
wn.setup(width=660, height=740)
wn.tracer(0) # Turns off the screen updates

# Draw Grid
grid_pen = turtle.Turtle()
grid_pen.speed(0)
grid_pen.color("darkgreen")
grid_pen.penup()
grid_pen.hideturtle()

for x in range(-300, 301, 20):
    grid_pen.goto(x, 300)
    grid_pen.pendown()
    grid_pen.goto(x, -300)
    grid_pen.penup()

for y in range(-300, 301, 20):
    grid_pen.goto(-300, y)
    grid_pen.pendown()
    grid_pen.goto(300, y)
    grid_pen.penup()

# RL Configuration
q_table = {}
alpha = 0.1      # Learning rate
gamma = 0.9      # Discount factor
epsilon = 0.1    # Exploration rate
actions = ["up", "down", "left", "right"]

# Snake head
head = turtle.Turtle()
head.speed(0)
head.shape("square")
head.color("black")
head.penup()
head.goto(0,0)
head.direction = "stop"

# Snake food
food = turtle.Turtle()
food.speed(0)
food.shape("circle")
food.color("red")
food.penup()
food.goto(0,100)

segments = []

# Pen
pen = turtle.Turtle()
pen.speed(0)
pen.shape("square")
pen.color("white")
pen.penup()
pen.hideturtle()
pen.goto(0, 310)
pen.write("Score: 0  High: 0  Rew: 0  MaxRew: 0  Gen: 1", align="center", font=("Courier", 14, "normal"))

# Exit Button
exit_pen = turtle.Turtle()
exit_pen.speed(0)
exit_pen.color("red")
exit_pen.penup()
exit_pen.hideturtle()
exit_pen.goto(0, -340)
exit_pen.write("EXIT", align="center", font=("Courier", 14, "bold"))

# Pause Button
pause_pen = turtle.Turtle()
pause_pen.speed(0)
pause_pen.color("white")
pause_pen.penup()
pause_pen.hideturtle()
pause_pen.goto(150, -340)
pause_pen.write("PAUSE", align="center", font=("Courier", 14, "bold"))

# Q-Value Visualization Pen
q_pen = turtle.Turtle()
q_pen.speed(0)
q_pen.color("yellow")
q_pen.penup()
q_pen.hideturtle()

# Functions
def get_state():
    # Head coordinates
    hx, hy = head.xcor(), head.ycor()
    fx, fy = food.xcor(), food.ycor()
    
    # Check for danger in immediate directions
    # Danger is: Wall or Body Segment
    def is_danger(x, y):
        if x > 290 or x < -290 or y > 290 or y < -290:
            return True
        for seg in segments:
            if seg.distance(x, y) < 20:
                return True
        return False

    danger_up = is_danger(hx, hy + 20)
    danger_down = is_danger(hx, hy - 20)
    danger_left = is_danger(hx - 20, hy)
    danger_right = is_danger(hx + 20, hy)

    # Food direction
    food_up = fy > hy
    food_down = fy < hy
    food_left = fx < hx
    food_right = fx > hx

    return (danger_up, danger_down, danger_left, danger_right, 
            food_up, food_down, food_left, food_right)

def choose_action(state):
    if random.uniform(0, 1) < epsilon:
        return random.choice(actions)
    
    if state not in q_table:
        q_table[state] = {a: 0 for a in actions}
    
    # Return action with max Q value
    return max(q_table[state], key=q_table[state].get)

def update_q_table(state, action, reward, next_state):
    if state not in q_table:
        q_table[state] = {a: 0 for a in actions}
    if next_state not in q_table:
        q_table[next_state] = {a: 0 for a in actions}
        
    old_value = q_table[state][action]
    next_max = max(q_table[next_state].values())
    
    new_value = (1 - alpha) * old_value + alpha * (reward + gamma * next_max)
    q_table[state][action] = new_value

def save_q_table():
    with open(Q_TABLE_FILE, "wb") as f:
        pickle.dump(q_table, f)

def load_q_table():
    global q_table
    if os.path.exists(Q_TABLE_FILE):
        with open(Q_TABLE_FILE, "rb") as f:
            q_table = pickle.load(f)
        print("Q-Table loaded.")
    else:
        print("No Q-Table file found. Starting new.")

def reset_game():
    global score, delay, episode_reward, generation
    
    # Log generation data
    with open(LOG_FILE, "a") as f:
        f.write("Gen: {}, Score: {}, Reward: {:.2f}\n".format(generation, score, episode_reward))

    save_q_table()
    time.sleep(0.1)
    head.goto(0,0)
    head.direction = "stop"

    # Hide the segments
    for segment in segments:
        segment.goto(1000, 1000)
    
    # Clear the segments list
    segments.clear()

    # Reset the score
    score = 0
    delay = 0.001
    episode_reward = 0
    generation += 1
    
    # Display update handled in main loop

def go_up():
    if head.direction != "down":
        head.direction = "up"

def go_down():
    if head.direction != "up":
        head.direction = "down"

def go_left():
    if head.direction != "right":
        head.direction = "left"

def go_right():
    if head.direction != "left":
        head.direction = "right"

# Keyboard bindings (Disabled for RL Agent)
# wn.listen()
# wn.onkeypress(go_up, "w")
# wn.onkeypress(go_down, "s")
# wn.onkeypress(go_left, "a")
# wn.onkeypress(go_right, "d")

def move():
    if head.direction == "up":
        y = head.ycor()
        head.sety(y + 20)

    if head.direction == "down":
        y = head.ycor()
        head.sety(y - 20)

    if head.direction == "left":
        x = head.xcor()
        head.setx(x - 20)

    if head.direction == "right":
        x = head.xcor()
        head.setx(x + 20)

# Menu System
menu_pen = turtle.Turtle()
menu_pen.speed(0)
menu_pen.shape("square")
menu_pen.color("white")
menu_pen.penup()
menu_pen.hideturtle()

def draw_button(x, y, text):
    menu_pen.goto(x, y - 10)
    menu_pen.write(text, align="center", font=("Courier", 16, "bold"))
    
    # Draw box
    menu_pen.goto(x - 70, y + 20)
    menu_pen.pendown()
    for _ in range(2):
        menu_pen.forward(140)
        menu_pen.right(90)
        menu_pen.forward(50)
        menu_pen.right(90)
    menu_pen.penup()

draw_button(-100, 0, "Load Q-Table")
draw_button(100, 0, "New Q-Table")

game_started = False

def on_click(x, y):
    global game_started, q_table
    if game_started: return

    # Check Load Button (-170 to -30, -30 to 20)
    if -170 < x < -30 and -30 < y < 20:
        load_q_table()
        game_started = True
        menu_pen.clear()
    
    # Check New Button (30 to 170, -30 to 20)
    elif 30 < x < 170 and -30 < y < 20:
        game_started = True
        menu_pen.clear()

wn.listen()
wn.onclick(on_click)

while not game_started:
    wn.update()
    time.sleep(0.1)

# Game Loop Control
keep_running = True

def on_game_click(x, y):
    global keep_running, paused
    # Check Exit Button (centered below grid)
    if -50 < x < 50 and -360 < y < -320:
        print("Saving Q-Table and Exiting...")
        save_q_table()
        keep_running = False
    
    # Check Pause Button
    if 100 < x < 200 and -360 < y < -320:
        paused = not paused
        pause_pen.clear()
        if paused:
            pause_pen.write("RESUME", align="center", font=("Courier", 14, "bold"))
        else:
            pause_pen.write("PAUSE", align="center", font=("Courier", 14, "bold"))

# Enable game click handler
wn.onclick(on_game_click)

# Main game loop
prev_dist = head.distance(food)

while keep_running:
    wn.update()

    if paused:
        time.sleep(0.1)
        continue

    # 1. Get current state
    current_state = get_state()

    # Visualize Q-values around the head
    q_pen.clear()
    vals = q_table.get(current_state, {a: 0 for a in actions})
    hx, hy = head.xcor(), head.ycor()
    
    # Draw values (Up, Down, Left, Right)
    q_pen.goto(hx, hy + 30)
    q_pen.write(f"{vals['up']:.1f}", align="center", font=("Arial", 8, "bold"))
    q_pen.goto(hx, hy - 40)
    q_pen.write(f"{vals['down']:.1f}", align="center", font=("Arial", 8, "bold"))
    q_pen.goto(hx - 30, hy - 10)
    q_pen.write(f"{vals['left']:.1f}", align="right", font=("Arial", 8, "bold"))
    q_pen.goto(hx + 30, hy - 10)
    q_pen.write(f"{vals['right']:.1f}", align="left", font=("Arial", 8, "bold"))

    # 2. Choose action
    action = choose_action(current_state)
    
    # 3. Perform action
    if action == "up": go_up()
    elif action == "down": go_down()
    elif action == "left": go_left()
    elif action == "right": go_right()

    # Move the end segments first in reverse order
    for index in range(len(segments)-1, 0, -1):
        x = segments[index-1].xcor()
        y = segments[index-1].ycor()
        segments[index].goto(x, y)

    # Move segment 0 to where the head is
    if len(segments) > 0:
        x = head.xcor()
        y = head.ycor()
        segments[0].goto(x,y)

    move()

    # 4. Calculate Reward & Check Collisions
    reward = -0.1 # Small penalty for each step to encourage speed
    done = False

    # Reward for moving towards food
    new_dist = head.distance(food)
    if new_dist < prev_dist:
        reward += 1
    else:
        reward -= 1.5
    prev_dist = new_dist

    # Check for a collision with the border
    if head.xcor()>290 or head.xcor()<-290 or head.ycor()>290 or head.ycor()<-290:
        reward = -100
        done = True

    # Check for head collision with the body segments
    for segment in segments:
        if segment.distance(head) < 20:
            reward = -100
            done = True
            break

    # Check for a collision with the food
    if head.distance(food) < 20:
        # Move the food to a random spot
        x = random.randint(-14, 14) * 20 # Align to grid
        y = random.randint(-14, 14) * 20
        food.goto(x,y)

        # Add a segment
        new_segment = turtle.Turtle()
        new_segment.speed(0)
        new_segment.shape("square")
        new_segment.color("grey")
        new_segment.penup()
        segments.append(new_segment)

        # Shorten the delay
        # delay -= 0.001 # Keep constant speed for RL

        # Increase the score
        score += 10
        reward = 50 # Big reward for eating
        prev_dist = head.distance(food) # Reset distance for new food

        if score > high_score:
            high_score = score
        
        # Display update handled at end of loop

    # Update accumulated reward
    episode_reward += reward
    if episode_reward > max_episode_reward:
        max_episode_reward = episode_reward

    # 5. Update Q-Table
    next_state = get_state()
    update_q_table(current_state, action, reward, next_state)

    # Update UI
    pen.clear()
    pen.write("Score: {}  High: {}  Rew: {:.0f}  MaxRew: {:.0f}  Gen: {}".format(score, high_score, episode_reward, max_episode_reward, generation), align="center", font=("Courier", 14, "normal"))

    if done:
        reset_game()
        prev_dist = head.distance(food)

    time.sleep(delay)

try:
    wn.bye()
except:
    pass