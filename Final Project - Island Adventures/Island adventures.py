import pygame
import sys
import os

# Initialize pygame
pygame.init()

# Screen stuff
screen_width = 1000
screen_height = 700
world_width = 1600
world_height = 1200

# Player stuff
player_x = 800
player_y = 600
old_player_x = 0
old_player_y = 0
player_speed = 1.5
zoom_level = 3
animation_timer = 0
current_frame = 0
is_moving = False
facing_right = True

# Game states
current_screen = "menu"  # can be "menu", "game", or "pong"

# UI stuff
show_shop = False
show_quest_list = False
show_talking = False
current_character = None
player_money = 0
quest_scroll_position = 0
max_scroll = 0

# Lists to hold game objects
collision_boxes = []
player_pictures = []
ui_icons = []
all_characters = []

# Pong game variables
ball_x = screen_width // 2
ball_y = screen_height // 2
ball_speed_x = 3
ball_speed_y = 3
player_paddle_position = screen_height // 2 - 50
computer_paddle_position = screen_height // 2 - 50
computer_score = 0
player_score = 0
paddle_width = 15
paddle_height = 100

# Load background music
pygame.mixer.init()
pygame.mixer.music.load("soundtrack1.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)  # play forever

# Quest list - each quest has: id, name, description, finished, unlocked
quest_list = [
    [1, "Welcome to the Island", "Talk to the Village Elder", False, True],
    [2, "Find the cat", "Help the crazy cat lady find her cat!", False, False],
    [3, "Fish for Dinner", "Catch 3 fish from the lake", False, False],
]

# Character list - each character has: name, x, y, image file, what they say, quest to unlock, quest to finish
character_info = [
    ["Village Elder", 620, 200, "elder.png",
     "Welcome to our island! I see that you were washed up here, well not to worry, because there is a way out, Complete quests and go talk to the man by the port",
     None, 1],

    ["Cat Lady", 1200, 250, "catlady.png",
     "Oh! thank goodness you're here... can you help me find my cat?",
     2, None],

    ["Island Cook", 790, 800, "cook.png",
     "I'm so hungry! Could you talk to the Fisherman and get me some fish?",
     3, None],

    ["Fisherman", 200, 500, "fisherman.png",
     "Here's the fish you needed!",
     None, 3],

    ["Cat", 300, 200, "cat.png",
     "You found the Cat ladies cat!",
     None, 2],

    ["Drunk Villager", 1000, 1000, "drunkguy.png",
     "Hey you lazy guy go finish your quests and then we can talk",
     None, None],
]


# Function to load all the character pictures and info (AI was used to help make this, but I fully understand what going on
def setup_characters():
    global all_characters
    all_characters = []

    # Go through each character in the list
    for char in character_info:
        name = char[0]
        char_x = char[1]
        char_y = char[2]
        picture_file = char[3]
        what_they_say = char[4]
        quest_to_unlock = char[5]
        quest_to_complete = char[6]

        # Load their picture
        character_picture = pygame.image.load(picture_file).convert_alpha()
        character_picture = pygame.transform.scale(character_picture, (60, 80))

        # Make a dictionary to store all their info
        character_dict = {
            'name': name,
            'x': char_x,
            'y': char_y,
            'picture': character_picture,
            'dialogue': what_they_say,
            'unlock_quest': quest_to_unlock,
            'complete_quest': quest_to_complete,
            'has_talked': False
        }

        all_characters.append(character_dict)


# Check if player is close to any character
def check_if_near_character():
    player_center_x = player_x + 35
    player_center_y = player_y + 50

    for character in all_characters:
        character_center_x = character['x'] + 30
        character_center_y = character['y'] + 40

        # Use distance formula to see how far apart they are (This was suggested by chatgpt)
        distance = ((player_center_x - character_center_x) ** 2 + (player_center_y - character_center_y) ** 2) ** 0.5

        if distance <= 80:  # distance where you should see the popup
            return character
    return None


# Start talking to a character
def start_talking_to_character(character):
    global show_talking, current_character, current_screen

    # Special case for the drunk guy - he needs all quests done first
    if character['name'] == "Drunk Villager":
        all_quests_done = True
        for quest in quest_list:
            if not quest[3]:  # If any quest is not finished
                all_quests_done = False
                break
            #Used chatgpt help to create the method to check if you have done your quests or not
        if not all_quests_done:
            show_talking = True
            current_character = {
                'name': "Drunk Villager",
                'dialogue': "Hey you lazy guy go finish your quests and then we can talk",
                'has_talked': True
            }
            return
        else:  # All quests are done
            show_talking = True
            current_character = {
                'name': "Drunk Villager",
                'dialogue': "Alright, you did it, you did all your quests, so im gonna help you get off this island, but first your gonna have to fight me in a game of pong",
                'has_talked': True
            }
            return

    # Normal talking for everyone else
    show_talking = True
    current_character = character

    # Do quest stuff if they haven't talked before
    if not character['has_talked']:
        if character['unlock_quest']:
            unlock_quest(character['unlock_quest'])
        if character['complete_quest']:
            finish_quest(character['complete_quest'])
        character['has_talked'] = True


# Draw the pong game(Claude ai helped with issues, but mostly done by me
def draw_pong_game():
    screen.fill((0, 0, 0))  # Black background

    # Draw the paddles
    pygame.draw.rect(screen, (255, 255, 255), (50, player_paddle_position, paddle_width, paddle_height))
    pygame.draw.rect(screen, (255, 255, 255),(screen_width - 65, computer_paddle_position, paddle_width, paddle_height))

    # Draw the ball
    pygame.draw.circle(screen, (255, 255, 255), (int(ball_x), int(ball_y)), 10)

    # Draw the center line
    for i in range(0, screen_height, 20):
        pygame.draw.rect(screen, (255, 255, 255), (screen_width // 2 - 2, i, 4, 10))

    # Draw the scores
    score_text = big_font.render(f"{player_score}    {computer_score}", True, (255, 255, 255))
    screen.blit(score_text, (screen_width // 2 - 30, 50))

    pygame.display.flip()


# Update the pong game
def update_pong_game():
    global ball_x, ball_y, ball_speed_x, ball_speed_y, computer_score, player_score, current_screen, computer_paddle_position

    # Move the ball
    ball_x += ball_speed_x
    ball_y += ball_speed_y

    # Bounce off top and bottom
    if ball_y <= 10 or ball_y >= screen_height - 10:
        ball_speed_y = -ball_speed_y

    # Move computer paddle (but make it slower as it gets more points)
    if computer_score < 5:
        if computer_paddle_position + paddle_height // 2 < ball_y:
            computer_paddle_position += 2
        elif computer_paddle_position + paddle_height // 2 > ball_y:
            computer_paddle_position -= 2

    # Check if ball hits paddles
    if (ball_x <= 65 and ball_y >= player_paddle_position and ball_y <= player_paddle_position + paddle_height):
        ball_speed_x = -ball_speed_x
    elif (
            ball_x >= screen_width - 75 and ball_y >= computer_paddle_position and ball_y <= computer_paddle_position + paddle_height):
        ball_speed_x = -ball_speed_x
        computer_score += 1

    # Check if ball goes off screen
    if ball_x < 0:
        computer_score += 1
        reset_pong_ball()
    elif ball_x > screen_width:
        player_score += 1
        reset_pong_ball()

    # Check if game is over
    if computer_score >= 5 and player_score >= 1:
        current_screen = "game"  # Go back to main game
        computer_score = 0
        player_score = 0


# Reset ball to center
def reset_pong_ball():
    global ball_x, ball_y
    ball_x = screen_width // 2
    ball_y = screen_height // 2


# Draw the talking window
def draw_talking_window():
    if not show_talking or not current_character:
        return

    # Dark overlay
    dark_overlay = pygame.Surface((screen_width, screen_height))
    #set the transparency level and color
    dark_overlay.set_alpha(128)
    dark_overlay.fill((0, 0, 0))
    screen.blit(dark_overlay, (0, 0))

    # Talking window
    window_width = 600
    window_height = 200
    window_x = screen_width // 2 - window_width // 2
    window_y = screen_height - window_height - 50

    pygame.draw.rect(screen, (240, 240, 240), (window_x, window_y, window_width, window_height))
    pygame.draw.rect(screen, (0, 0, 0), (window_x, window_y, window_width, window_height), 3)

    # Character name
    name_text = big_font.render(current_character['name'], True, (0, 0, 0))
    screen.blit(name_text, (window_x + 20, window_y + 15))

    # Close button
    close_button_x = window_x + window_width - 30
    close_button_y = window_y + 10
    pygame.draw.rect(screen, (255, 100, 100), (close_button_x, close_button_y, 20, 20))
    x_text = small_font.render("X", True, (255, 255, 255))
    screen.blit(x_text, (close_button_x + 6, close_button_y + 2))

    # Split up the dialogue text so it fits in the window(Needed chatgpt help because the text was going outside of the box
    dialogue_text = current_character['dialogue']
    max_width = window_width - 40
    words = dialogue_text.split(' ')
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + word + " "
        test_surface = small_font.render(test_line, True, (0, 0, 0))
        if test_surface.get_width() <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line.strip())
                current_line = word + " "
            else:
                lines.append(word)
                current_line = ""

    if current_line:
        lines.append(current_line.strip())

    # Draw the text lines
    line_spacing = 18
    start_y = window_y + 50
    for i, line in enumerate(lines):
        if start_y + (i * line_spacing) < window_y + window_height - 30:
            text_surface = small_font.render(line, True, (0, 0, 0))
            screen.blit(text_surface, (window_x + 20, start_y + (i * line_spacing)))

    # Special Let's Go button for the drunk guy when all quests are done
    all_quests_done = True
    for quest in quest_list:
        if not quest[3]:
            all_quests_done = False
            break

    if (current_character['name'] == "Drunk Villager" and all_quests_done and "im gonna help you get off this island" in
            current_character['dialogue']):
        button_width = 80
        button_height = 25
        button_x = window_x + window_width - button_width - 50
        button_y = window_y + window_height - button_height - 15

        pygame.draw.rect(screen, (100, 200, 100), (button_x, button_y, button_width, button_height))
        pygame.draw.rect(screen, (0, 0, 0), (button_x, button_y, button_width, button_height), 2)

        button_text = small_font.render("Let's Go!", True, (0, 0, 0))
        text_rect = button_text.get_rect(center=(button_x + button_width // 2, button_y + button_height // 2))
        screen.blit(button_text, text_rect)


# Unlock a quest
def unlock_quest(quest_id):
    for quest in quest_list:
        if quest[0] == quest_id:
            quest[4] = True  # Set unlocked to True
            break


# Complete a quest and give money
def finish_quest(quest_id):
    global player_money
    for quest in quest_list:
        if quest[0] == quest_id:
            if not quest[3]:  # Only give money if not already completed
                quest[3] = True  # Set completed to True
                player_money += 10  # Give 10 coins
            break


# Add money to player
def give_player_money(amount):
    global player_money
    player_money += amount


# Set up all the game stuff
def setup_game():
    global screen, world_surface, background_image, menu_button_image, title_image, coin_image, big_font, small_font

    # Create the screen
    screen = pygame.display.set_mode((screen_width, screen_height))
    world_surface = pygame.Surface((world_width, world_height))
    pygame.display.set_caption("Island Adventures")

    # Load fonts
    big_font = pygame.font.Font(None, 24)
    small_font = pygame.font.Font(None, 18)

    # Make a simple coin image
    coin_image = pygame.Surface((30, 30), pygame.SRCALPHA)
    pygame.draw.circle(coin_image, (255, 215, 0), (15, 15), 15)
    pygame.draw.circle(coin_image, (255, 255, 0), (15, 15), 12)

    # Load menu button
    menu_button_image = pygame.image.load("Startbutton.png").convert_alpha()
    menu_button_image = pygame.transform.scale(menu_button_image, (500, 400))

    # Load title
    title_image = pygame.image.load("title.png").convert()
    title_image = pygame.transform.scale(title_image, (screen_width, screen_height))

    # Load UI icons
    icon_image = pygame.image.load("icon.png").convert_alpha()
    icon_image = pygame.transform.scale(icon_image, (150, 300))

    global ui_icons
    ui_icons = []
    for i in range(3):
        icon = icon_image.subsurface((0, i * 100, 150, 100)).copy()
        ui_icons.append(icon)

    # Load background map
    background_image = pygame.image.load("Map.png").convert()
    background_image = pygame.transform.scale(background_image, (world_width, world_height))

    # Load collision data from file(Chatgpt)
    if os.path.exists("collision_rectangles.txt"):
        collision_file = open("collision_rectangles.txt", 'r')
        lines = collision_file.readlines()
        collision_file.close()
        for line in lines:
            if "x=" in line:
                parts = line.split(": ")[1]
                x_value = int(parts.split("x=")[1].split(",")[0])
                y_value = int(parts.split("y=")[1].split(",")[0])
                width_value = int(parts.split("w=")[1].split(",")[0])
                height_value = int(parts.split("h=")[1])
                collision_boxes.append([x_value, y_value, width_value, height_value])

    # Load player images
    player_image1 = pygame.image.load("Front_player.png").convert_alpha()
    player_image1 = pygame.transform.scale(player_image1, (70, 100))
    player_image2 = pygame.image.load("Anim1.png").convert_alpha()
    player_image2 = pygame.transform.scale(player_image2, (70, 100))
    player_image3 = pygame.image.load("Anim2.png").convert_alpha()
    player_image3 = pygame.transform.scale(player_image3, (70, 100))
    global player_pictures
    player_pictures = [player_image1, player_image2, player_image3]

    # Load all the characters
    setup_characters()


# Draw the menu screen
def draw_menu_screen():
    screen.blit(title_image, (0, 0))
    button_x = (screen_width - menu_button_image.get_width()) // 2
    button_y = 350
    screen.blit(menu_button_image, (button_x, button_y))
    pygame.display.flip()
    return button_x, button_y


# Check if start button was clicked
def check_start_button_click(mouse_position, button_x, button_y):
    global current_screen
    button_rectangle = pygame.Rect(button_x, button_y, 500, 400)
    if button_rectangle.collidepoint(mouse_position):
        current_screen = "game"


# Check if UI icons were clicked
def check_icon_clicks(mouse_position):
    global show_shop, show_quest_list, current_screen, quest_scroll_position
    icon_x = screen_width - 150
    icon_y_start = 250
    for i in range(len(ui_icons)):
        icon_y = icon_y_start + (i * 100)
        icon_rectangle = pygame.Rect(icon_x, icon_y, 150, 100)
        if icon_rectangle.collidepoint(mouse_position):
            if i == 0:  # Quest icon
                show_quest_list = not show_quest_list
                show_shop = False
                quest_scroll_position = 0
            elif i == 1:  # Shop icon
                show_shop = not show_shop
                show_quest_list = False
            elif i == 2:  # Menu icon
                current_screen = "menu"
                show_shop = False
                show_quest_list = False
            break


# Check if close buttons were clicked on windows
def check_close_button_clicks(mouse_position):
    global show_shop, show_quest_list, show_talking, current_character, current_screen

    if show_talking:
        window_width = 600
        window_x = screen_width // 2 - window_width // 2
        window_y = screen_height - 200 - 50

        # Check Let's Go button for drunk guy
        all_quests_done = True
        for quest in quest_list:
            if not quest[3]:
                all_quests_done = False
                break

        if (current_character[
            'name'] == "Drunk Villager" and all_quests_done and "im gonna help you get off this island" in
                current_character['dialogue']):
            button_width = 80
            button_height = 25
            button_x = window_x + window_width - button_width - 50
            button_y = window_y + 200 - button_height - 15

            if pygame.Rect(button_x, button_y, button_width, button_height).collidepoint(mouse_position):
                show_talking = False
                current_character = None
                current_screen = "pong"
                return True

        # Regular close button
        close_x = window_x + window_width - 30
        close_y = window_y + 10
        if pygame.Rect(close_x, close_y, 20, 20).collidepoint(mouse_position):
            show_talking = False
            current_character = None
            return True

    if show_shop:
        close_x = screen_width // 2 + 200 - 30
        close_y = screen_height // 2 - 150 + 10
        if pygame.Rect(close_x, close_y, 20, 20).collidepoint(mouse_position):
            show_shop = False
            return True

    if show_quest_list:
        close_x = screen_width // 2 + 200 - 30
        close_y = screen_height // 2 - 150 + 10
        if pygame.Rect(close_x, close_y, 20, 20).collidepoint(mouse_position):
            show_quest_list = False
            return True
    return False


# Draw the shop window
def draw_shop_window():
    # Dark overlay behind window
    overlay = pygame.Surface((screen_width, screen_height))
    overlay.set_alpha(128)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    window_width = 600
    window_height = 400
    window_x = screen_width // 2 - window_width // 2
    window_y = screen_height // 2 - window_height // 2

    pygame.draw.rect(screen, (200, 200, 200), (window_x, window_y, window_width, window_height))
    pygame.draw.rect(screen, (0, 0, 0), (window_x, window_y, window_width, window_height), 3)

    title_text = big_font.render("Shop", True, (0, 0, 0))
    screen.blit(title_text, (window_x + 20, window_y + 20))

    # Show money in shop
    money_text = small_font.render(f"Coins: {player_money}", True, (255, 215, 0))
    screen.blit(money_text, (window_x + window_width - 120, window_y + 20))

    # Close button
    close_x = window_x + window_width - 30
    close_y = window_y + 10
    pygame.draw.rect(screen, (255, 100, 100), (close_x, close_y, 20, 20))
    x_text = small_font.render("X", True, (255, 255, 255))
    screen.blit(x_text, (close_x + 6, close_y + 2))

    # Draw empty item slots
    slot_size = 80
    slots_per_row = 6
    start_x = window_x + 30
    start_y = window_y + 60

    for row in range(4):
        for col in range(slots_per_row):
            slot_x = start_x + (col * (slot_size + 10))
            slot_y = start_y + (row * (slot_size + 10))

            # Draw empty slot
            pygame.draw.rect(screen, (150, 150, 150), (slot_x, slot_y, slot_size, slot_size))
            pygame.draw.rect(screen, (100, 100, 100), (slot_x, slot_y, slot_size, slot_size), 2)

            # Add "Empty" text
            empty_text = small_font.render("Empty", True, (80, 80, 80))
            text_rect = empty_text.get_rect(center=(slot_x + slot_size // 2, slot_y + slot_size // 2))
            screen.blit(empty_text, text_rect)


# Draw the quest window
def draw_quest_window():
    global max_scroll
    # Dark overlay behind window
    overlay = pygame.Surface((screen_width, screen_height))
    overlay.set_alpha(128)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    window_width = 500
    window_height = 400
    window_x = screen_width // 2 - window_width // 2
    window_y = screen_height // 2 - window_height // 2

    pygame.draw.rect(screen, (200, 200, 200), (window_x, window_y, window_width, window_height))
    pygame.draw.rect(screen, (0, 0, 0), (window_x, window_y, window_width, window_height), 3)

    title_text = big_font.render("Quests", True, (0, 0, 0))
    screen.blit(title_text, (window_x + 20, window_y + 20))

    # Close button
    close_x = window_x + window_width - 30
    close_y = window_y + 10
    pygame.draw.rect(screen, (255, 100, 100), (close_x, close_y, 20, 20))
    x_text = small_font.render("X", True, (255, 255, 255))
    screen.blit(x_text, (close_x + 6, close_y + 2))

    # Scroll area
    scroll_area = pygame.Rect(window_x + 10, window_y + 60, window_width - 20, window_height - 70)
    pygame.draw.rect(screen, (255, 255, 255), scroll_area)
    pygame.draw.rect(screen, (0, 0, 0), scroll_area, 2)

    # Get only unlocked quests
    unlocked_quests = []
    for quest in quest_list:
        if quest[4]:  # If unlocked
            unlocked_quests.append(quest)

    quest_height = len(unlocked_quests) * 80
    max_scroll = max(0, quest_height - (window_height - 70))

    y_position = scroll_area.y + 10 - quest_scroll_position
    for quest in unlocked_quests:
        if y_position > scroll_area.bottom:
            break
        if y_position + 70 > scroll_area.top:
            quest_rect = pygame.Rect(scroll_area.x + 10, y_position, scroll_area.width - 20, 70)
            # Green background if completed, white if not
            color = (220, 255, 220) if quest[3] else (255, 255, 255)
            pygame.draw.rect(screen, color, quest_rect)
            pygame.draw.rect(screen, (0, 0, 0), quest_rect, 1)

            # Checkbox
            check_x = quest_rect.x + 10
            check_y = quest_rect.y + 10
            if quest[3]:  # If completed
                pygame.draw.rect(screen, (0, 200, 0), (check_x, check_y, 20, 20))
                # Draw checkmark
                pygame.draw.line(screen, (255, 255, 255), (check_x + 4, check_y + 10), (check_x + 8, check_y + 14), 2)
                pygame.draw.line(screen, (255, 255, 255), (check_x + 8, check_y + 14), (check_x + 16, check_y + 6), 2)
            else:
                pygame.draw.rect(screen, (255, 255, 255), (check_x, check_y, 20, 20))
                pygame.draw.rect(screen, (0, 0, 0), (check_x, check_y, 20, 20), 2)

            # Quest text
            title_text = small_font.render(quest[1], True, (0, 0, 0))
            screen.blit(title_text, (check_x + 30, quest_rect.y + 5))
            description_text = small_font.render(quest[2], True, (100, 100, 100))
            screen.blit(description_text, (check_x + 30, quest_rect.y + 25))
            status_text = "COMPLETED" if quest[3] else "IN PROGRESS"
            status_color = (0, 150, 0) if quest[3] else (150, 150, 0)
            status_surface = small_font.render(status_text, True, status_color)
            screen.blit(status_surface, (check_x + 30, quest_rect.y + 45))
        y_position += 80


# Draw the money counter
def draw_money_display():
    coin_x = 20
    coin_y = 20
    screen.blit(coin_image, (coin_x, coin_y))
    money_text = big_font.render(f"{player_money:03d}", True, (255, 215, 0))
    screen.blit(money_text, (coin_x + 40, coin_y + 5))


# Show hint when near character
def draw_talk_hint():
    nearby_character = check_if_near_character()
    if nearby_character and not show_talking:
        hint_text = small_font.render(f"Press E to talk to {nearby_character['name']}", True, (255, 255, 255))
        hint_rect = hint_text.get_rect(center=(screen_width // 2, 100))
        background_rect = hint_rect.inflate(20, 10)
        pygame.draw.rect(screen, (0, 0, 0, 180), background_rect)
        pygame.draw.rect(screen, (255, 255, 255), background_rect, 2)
        screen.blit(hint_text, hint_rect)


# Check what keys are pressed for movement
def check_movement_keys():
    global player_x, player_y, old_player_x, old_player_y, is_moving, facing_right
    keys = pygame.key.get_pressed()
    is_moving = False  # Reset movement
    old_player_x = player_x  # Save old position
    old_player_y = player_y

    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        player_x = player_x - player_speed
        is_moving = True

        facing_right = False
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player_x = player_x + player_speed
        is_moving = True
        facing_right = True
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        player_y = player_y - player_speed
        is_moving = True
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        player_y = player_y + player_speed
        is_moving = True


# Check for collisions and fix player position
def check_collisions():
    global player_x, player_y

    # Test the new position before committing to it
    test_rect = pygame.Rect(player_x + 20, player_y + 80, 30, 20)  # Just the feet

    collision_detected = False
    for collision_box in collision_boxes:
        collision_rect = pygame.Rect(collision_box[0], collision_box[1], collision_box[2], collision_box[3])
        if test_rect.colliderect(collision_rect):
            collision_detected = True
            break

    if collision_detected:
        # Reset to old position
        player_x = old_player_x
        player_y = old_player_y

    # Keep player within world bounds
    if player_x < 0:
        player_x = 0
    if player_x > world_width - 70:
        player_x = world_width - 70
    if player_y < 0:
        player_y = 0
    if player_y > world_height - 100:
        player_y = world_height - 100


# Update player animation
def update_animation():
    global animation_timer, current_frame
    if is_moving:
        animation_timer += 1
        if animation_timer >= 20:  # Change frame every 20 game loops
            animation_timer = 0
            # Only cycle between frames 1 and 2 (the walking frames)
            if current_frame == 1:
                current_frame = 2
            else:
                current_frame = 1
    else:
        current_frame = 0  # Front-facing frame when standing still


# Draw everything on the world surface
def draw_world():
    # Draw background
    world_surface.blit(background_image, (0, 0))

    # Draw all characters
    for character in all_characters:
        world_surface.blit(character['picture'], (character['x'], character['y']))

    # Draw player with correct animation frame
    player_image = player_pictures[current_frame]
    if not facing_right:
        player_image = pygame.transform.flip(player_image, True, False)
    world_surface.blit(player_image, (player_x, player_y))


# Calculate camera position to follow player
def calculate_camera():
    # Center the camera on the player
    # Player center should be at screen center
    view_width = screen_width // zoom_level
    view_height = screen_height // zoom_level

    player_center_x = player_x + 35  # Half of player width (70/2)
    player_center_y = player_y + 50  # Half of player height (100/2)

    camera_x = player_center_x - view_width // 2
    camera_y = player_center_y - view_height // 2

    # Keep camera within world bounds
    camera_x = max(0, min(camera_x, world_width - view_width))
    camera_y = max(0, min(camera_y, world_height - view_height))

    return int(camera_x), int(camera_y)


# Draw the game screen
def draw_game_screen():
    camera_x, camera_y = calculate_camera()

    # Create a subsurface of the world to show
    view_width = screen_width // zoom_level
    view_height = screen_height // zoom_level
    view_surface = world_surface.subsurface((camera_x, camera_y, view_width, view_height))

    # Scale it up and draw to screen
    scaled_surface = pygame.transform.scale(view_surface, (screen_width, screen_height))
    screen.blit(scaled_surface, (0, 0))

    # Draw UI on top
    draw_money_display()
    draw_talk_hint()

    # Draw UI icons
    icon_x = screen_width - 150
    icon_y_start = 250
    for i, icon in enumerate(ui_icons):
        icon_y = icon_y_start + (i * 100)
        screen.blit(icon, (icon_x, icon_y))

    # Draw windows if they're open
    if show_shop:
        draw_shop_window()
    if show_quest_list:
        draw_quest_window()
    if show_talking:
        draw_talking_window()


# Main game loop
def main():
    global current_screen, quest_scroll_position, player_paddle_position
    global show_talking, show_shop, show_quest_list, current_character

    setup_game()
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if current_screen == "menu":
                    button_x, button_y = draw_menu_screen()
                    check_start_button_click(event.pos, button_x, button_y)
                elif current_screen == "game":
                    if not check_close_button_clicks(event.pos):
                        check_icon_clicks(event.pos)

            elif event.type == pygame.KEYDOWN:
                if current_screen == "game":
                    if event.key == pygame.K_e:
                        nearby_character = check_if_near_character()
                        if nearby_character and not show_talking:
                            start_talking_to_character(nearby_character)
                    elif event.key == pygame.K_ESCAPE:
                        show_shop = False
                        show_quest_list = False
                        show_talking = False
                        current_character = None

                elif current_screen == "pong":
                    if event.key == pygame.K_ESCAPE:
                        current_screen = "game"

            elif event.type == pygame.MOUSEWHEEL:
                if show_quest_list:
                    quest_scroll_position -= event.y * 20
                    quest_scroll_position = max(0, min(quest_scroll_position, max_scroll))

        # Handle different screens
        if current_screen == "menu":
            draw_menu_screen()

        elif current_screen == "game":
            # Update game logic
            check_movement_keys()
            check_collisions()
            update_animation()
            draw_world()
            draw_game_screen()

        elif current_screen == "pong":
            # Handle pong paddle movement
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP] and player_paddle_position > 0:
                player_paddle_position -= 3
            if keys[pygame.K_DOWN] and player_paddle_position < screen_height - paddle_height:
                player_paddle_position += 3

            update_pong_game()
            draw_pong_game()

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()