import tkinter as tk
from tkinter import messagebox
from collections import Counter
from time import sleep
import random
import os
import sys
import pygame
import math
import time
import asyncio


pygame.init()

screen_info = pygame.display.Info()

WIDTH, HEIGHT = screen_info.current_w, screen_info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("...")

base_luck = 0 # base luck of everything
bonus_roll = 0 # roll count till bonus roll
bonus_roll_multi = 2 # multiplier of bonus (-1 from intended multi)
bonus_roll_event = 10 #how many rolls needed for bonus_roll to trigger
bonus_roll_active = False # Check if bonus_roll_active is there
bonus_roll_label = '0/10'
rolls = 0

roll_cooldown = 1.2
timer_1 = 0

auto_active = False

till_luck_exp = 0 # counts how many rolls till lucky potion runs out
lucky_potion_used = 1
# for collection of items
previous_roll = 0

aura_inventory = {}
item_inventory = {}
owned_gears = []

file_path_aura = os.path.join('config', 'aura.txt')
file_path_gear = os.path.join('config', 'gear.txt')
file_path_items = os.path.join('config', 'item.txt')

try:
    aura_inventory = {}  # Initialize the dictionary to store auras
    try:
        with open(file_path_aura, 'r') as file:
            auras = file.read()
            aura_name = '' # stores key:value pairs
            temp_aura_name = ''
            for i in auras:
                if i == ':':
                    aura_inventory.update({aura_name: 0})
                    temp_aura_name = aura_name
                    aura_name = ''
                elif i == '|':
                    aura_inventory[temp_aura_name] += int(aura_name)
                    aura_name = ''
                    temp_aura_name = ''
                else:
                    aura_name += i
            print('Your previous save of auras: ' + str(aura_inventory))

            
        with open(file_path_gear, 'r') as file:
            gear = file.read()
            gear_name = '' # stores key:value pairs
            for i in gear:
                if i == '|':
                    owned_gears.append(gear_name)
                    gear_name = ''
                else:
                    gear_name += i
            print('Your previous save of gears: ' + str(owned_gears))
        
        with open(file_path_items, 'r') as file:
            items = file.read()
            item_name = '' # stores key:value pairs
            temp_item_name = ''
            for i in items:
                if i == ':':
                    item_inventory.update({item_name: 0})
                    temp_item_name = item_name
                    item_name = ''
                elif i == '|':
                    item_inventory[temp_item_name] += int(item_name)
                    item_name = ''
                    temp_item_name = ''
                else:
                    item_name += i
            print('Your previous save of items: ' + str(item_inventory))
    except KeyError:
        print('No aura/gears/items saved before!')
        aura_inventory = {}
    

            
except FileNotFoundError:
    print(f"No save file not found. Could it be that you have deleted the file by accident?")
    aura_inevntory = []


# COMPLETED
def roll_aura():
    global timer_1, roll_cooldown, lucky_potion_used, previous_roll, till_luck_exp, bonus_roll_multi, bonus_roll, bonus_roll_event, bonus_roll_label, lucky_potions, aura_inventory, file_path_aura, base_luck, rolls, bonus_roll_active
    
    #loot table
    auras = {
    #2-999
    'common (1 in 2)': 2,
    'uncommon (1 in 4)': 4,
    'rare (1 in 16)': 16,
    'divinus (1 in 32)': 32,
    'crystalised (1 in 64)': 64,
    'rage (1 in 128)': 128,
    'Emerald (1 in 300)': 300,
    'ruby (1 in 350)': 350,
    'gilded (1 in 512)': 512,
    'diamond (1 in 555)': 555,
    'windbreaker (1 in 900)': 800,
    'icebreaker (1 in 999)': 999,
    #1k-99k
    'diaboli (1 in 1004)': 1004,
    'voided (1 in 1010)': 1010,
    'glossy (1 in 1111)': 1111,
    'starry (1 in 2008)': 2008,
    'lunar (1 in 5000)': 5000,
    'solar (1 in 5000)': 5000,
    'scorched (1 in 6699)': 6699,
    'tide (1 in 7000)': 7000,
    
    }
    if time.time() - timer_1 <= roll_cooldown and rolls > 0:
        cooldown_show = time.time() - timer_1
        cooldown_show = "{:.1f}".format(cooldown_show)
        print(f"You are on roll cooldown! {cooldown_show} secs passed")
        return
    rolls += 1
    previous_roll += 1

    bonus_roll_calc = 0
    special_luck = 0
    if till_luck_exp == 1:
        print('lucky potion is expiring in 1 roll! Lucky potion effect status will not apply to the following roll')
        till_luck_exp -= 2
    elif till_luck_exp == -1:
        base_luck -= 0.4
        till_luck_exp += 1
    elif till_luck_exp == (lucky_potion_used - 1) * 25:
        if lucky_potion_used > 1:
            base_luck += 0.4
            print("lucky potion status has been applied for next 25 rolls!!!")
            till_luck_exp -= 1
        else:
            pass
    elif till_luck_exp > 0 and till_luck_exp != lucky_potion_used * 25:
        till_luck_exp -= 1
        lucky_potions_used = 1
        
    
    
    # bonus roll check
    
    if bonus_roll_active == True:
        bonus_roll_calc = bonus_roll_multi
        bonus_roll = 0
        bonus_roll_active = False
        bonus_roll_label = '0/10'
    elif bonus_roll == bonus_roll_event - 1:  # Bonus roll triggers on the next roll
        print(f"{bonus_roll_multi}x luck ready!")
        bonus_roll_label = f"{bonus_roll_multi}x luck ready!"
        bonus_roll_active = True
    else:
        bonus_roll += 1
        bonus_roll_label = f"{bonus_roll}/{bonus_roll_event}"
    #adjust luck by probability based on luck multi
    if bonus_roll_calc > 0:
        total_luck = (1 + base_luck) * bonus_roll_calc + special_luck
    else:
        total_luck = 1 + base_luck + special_luck
        
    #DEBUG: adjust total luck to intened luck of testing
    total_luck = 1000

    auras_to_remove = [aura for aura, weight in auras.items() if weight < total_luck]
    for aura in auras_to_remove:
        del auras[aura]
        #print(f"Removed aura: {aura}")
                
    
    weighted_auras = {
        aura: weight / total_luck for aura, weight in auras.items()
    }
    
    try:
        #covert numbers into percentages
        normalised_auras = {aura: 1 / weight for aura, weight in weighted_auras.items()}
    
        aura_names = list(normalised_auras.keys())
        aura_probabilities = list(normalised_auras.values())
        rolled_aura = random.choices(aura_names, weights=aura_probabilities, k=1)[0]


        palette = {
            "diaboli (1 in 1004)": (255, 0, 0),
            "voided (1 in 1010)": (22, 23, 22),
            'glossy (1 in 1111)': (193, 245, 241),
            'starry (1 in 2008)': (193, 245, 241),
            'lunar (1 in 5000)': (144, 74, 224),
            'solar (1 in 5000)': (245, 181, 54),
            'scorched (1 in 6699)': (125, 32, 32),
            'tide (1 in 7000)': (0, 200, 255), 
        }

        rarity = auras[rolled_aura]
        if rarity > 999:
            colour = palette[rolled_aura]
            point_cutscene(colour)
        
        result_label.config(text=f"You rolled: {rolled_aura}")
        print(f'{rolled_aura} at luck of {total_luck}')
        try:
            aura_inventory[rolled_aura] += 1
        except:
            #If it is a newly found aura
            aura_inventory.update({rolled_aura: 1}) 
            

        with open(file_path_aura, 'w') as file:
            for aura, count in aura_inventory.items():
                file.write(str(aura) + ":" + str(count) + "|")
        timer_1 = time.time()

    except IndexError:
        print('No auras to randomise!!!')
        print(auras)

    roll_button.config(text=f"Roll Aura {bonus_roll_label}")
    rolls_label.config(text=f"Rolls: {rolls}")
    
def roll_items():
    global item_inventory
    
    #loot table
    loot_item = {
    #2-999
    'lucky potion': 50,
    'speed potion': 25,
    'special_potion': 10
    }

    
    weighted_loot_item = {
        aura: weight for aura, weight in loot_item.items()
    }
    
    try:
        #covert numbers into percentages
        normalised_items = {aura: 1 / weight for aura, weight in weighted_loot_item.items()}
    
        item_names = list(normalised_items.keys())
        item_probabilities = list(normalised_items.values())
        rolled_item = random.choices(item_names, weights=item_probabilities, k=1)[0]

        
        result_label.config(text=f"You collected: {rolled_item}")
        try:
            item_inventory[rolled_item] += 1
        except:
            #If it is a newly found item
            item_inventory.update({rolled_item: 1}) 
            

        with open(file_path_items, 'w') as file:
            for item, count in item_inventory.items():
                file.write(str(item) + ":" + str(count) + "|")
                
        print(item_inventory)
        
    except IndexError:
        print('No items to randomise!!!')
        print(auras)

    
# COMPLETED: works as it should be
def button_1_action():
    roll_aura()
    
def button_2_action():
    global aura_inventory
    show_inventory = ''
    # Create a new window for inventory
    inventory_window = tk.Toplevel(root)
    inventory_window.title("Inventory")
    inventory_window.geometry("500x700")

    # TEMPORARY: Auras are not sorted out by rarity
    for aura, count in aura_inventory.items():
        show_inventory += f'\n{aura}: {count}'
    
    inventory_label = tk.Label(inventory_window, text=f"{show_inventory}", font=("Helvetica", 16), wraplength=400, justify="left")
    inventory_label.pack(pady=20)

# COMPLETED: Added one gear that can directly impact base_luck
def craft(gear):
    global base_luck, aura_inventory, owned_gears

    approve = 0
    if gear == 1: # Craft 'Lucky Gem'
        # check if all items are on deck
        for aura, count in aura_inventory.items():
            if aura == 'common (1 in 2)' and count >= 5:
                approve += 1
            if aura == 'uncommon (1 in 4)' and count >= 3 :
                approve += 1
            if aura == 'Emerald (1 in 300)' and count >= 1:
                approve += 1                   
        # delete auras necessary for crafting
        if 'lucky gem' in owned_gears:
            messagebox.showinfo("Gear Crafting", "You already owned this item!")
        elif approve == 3:
            for aura, count in aura_inventory.items():
                if aura == 'common (1 in 2)' and count >= 5:
                    aura_inventory['common (1 in 2)'] -= 5
                    print('5 commons has been deleted')
                if aura == 'uncommon (1 in 4)' and count >= 3 :
                    aura_inventory['uncommon (1 in 4)'] -= 3
                    print('3 uncommons has been deleted')                    
                if aura == 'Emerald (1 in 300)' and count >= 1:
                    aura_inventory['Emerald (1 in 300)'] -= 1
                    print('one emerald has been deleted')
            
            messagebox.showinfo("Gear Crafting", "\'Lucky Gem\' item has been crafted!")
            base_luck += 0.4
            owned_gears.append('lucky gem')
            with open(file_path_gear, 'w') as file:        
                for gear in owned_gears:
                    file.write('')
                    file.write(str(gear) + '|')
        else:
            messagebox.showinfo("Gear Crafting", "Insufficient materials for gear crafting!")

            
    if gear == 2: # Craft 'windbender'
        # check if all items are on deck
        for aura, count in aura_inventory.items():
            if aura == 'common (1 in 2)' and count >= 5:
                approve += 1
            if aura == 'uncommon (1 in 4)' and count >= 3 :
                approve += 1
            if aura == 'Emerald (1 in 300)' and count >= 1:
                approve += 1                   
        # delete auras necessary for crafting
        if 'windbender' in owned_gears:
            messagebox.showinfo("Gear Crafting", "You already owned this item!")
        elif approve == 3:
            for aura, count in aura_inventory.items():
                if aura == 'common (1 in 2)' and count >= 10:
                    aura_inventory['common (1 in 2)'] -= 10
                    print('10 commons has been deleted')
                if aura == 'uncommon (1 in 4)' and count >= 5 :
                    aura_inventory['uncommon (1 in 4)'] -= 5
                    print('5 uncommons has been deleted')                    
                if aura == 'windbreaker (1 in 900)' and count >= 2:
                    aura_inventory['windbreaker (1 in 900)'] -= 2
                    print('2 windbreaker has been deleted')
            
            messagebox.showinfo("Gear Crafting", "\'windbender\' item has been crafted!")
            base_luck += 0.5
            owned_gears.append('windbender')
            with open(file_path_gear, 'w') as file:        
                for gear in owned_gears:
                    file.write('')
                    file.write(str(gear) + '|')
        else:
            messagebox.showinfo("Gear Crafting", "Insufficient materials for gear crafting!")
def recipe():
    gear_window = tk.Toplevel(root)
    gear_window.title("Gear Recipe")
    gear_window.geometry("700x500")
    gear_label = tk.Label(gear_window, text="Lucky Gem: \n 5 commons | 3 uncommons | 1 emerald \n Windbender: \n 10 commons 5 uncommons 2 windbreaker", font=("Courier New", 16))
    gear_label.pack(pady=20)

# COMPLETED    
def button_3_action():
    global owned_gears
    # Create a new window for gear crafting
    gear_window = tk.Toplevel(root)
    gear_window.title("Craft Gears")
    gear_window.geometry("700x400")

    gear_label = tk.Label(gear_window, text="Craft a gear!", font=("Helvetica", 16))
    gear_label.pack(pady=20)

    # Create a frame
    left_frame = tk.Frame(gear_window, width=200)  # Explicitly define width
    left_frame.pack(side="left", padx=20, pady=20, fill="y")

    center_frame = tk.Frame(gear_window, width=250)  # Explicit width to ensure it doesn't shrink
    center_frame.pack(side="left", padx=20, pady=20, fill="y")
    
    # Prepare the owned gears list
    gear_show = ''
    for i in owned_gears:
        gear_show += i + " | "
        
    # Owned gears label
    gear_label_2 = tk.Label(center_frame, text=f"Owned gears: {gear_show}", font=("Helvetica", 16))
    gear_label_2.pack(pady=10)

    # Recipe Button
    check_recipe = tk.Button(
        center_frame, 
        text="recipes", 
        font=("Helvetica", 14), 
        command=lambda: recipe()  # Function to be triggered
    )
    check_recipe.pack(pady=10)

    # Add craft buttons
    craft_button_1 = tk.Button(
        left_frame, 
        text="Lucky gem | +40% luck", 
        font=("Helvetica", 14), 
        command=lambda: craft(1)  # Use lambda to pass the argument
    )
    craft_button_1.pack(pady=10)

    craft_button_2 = tk.Button(
        left_frame, 
        text="windbender | +70% luck", 
        font=("Helvetica", 14), 
        command=lambda: craft(2)  # Use lambda to pass the argument
    )
    craft_button_2.pack(pady=10)


    

def button_4_action():
    print("View Quests")


# settings fucntions (COMPLETED)
def reset_data():
    if messagebox.askyesno("DATA RESET: WIPE ALL YOUR DATA", "This action is irreversible. Proceed?") == True:
        print('Resetting data...')
        with open(file_path_aura, 'w') as file:
            file.write('')
        with open(file_path_gear, 'w') as file:
            file.write('')
        print('Data reset is completed! Your aura, gears, and potions inventory is now empty')
    else:
        messagebox.showinfo("Action cancelled", "Data reset process has been cancelled. No save files has been cleared")

        
def button_5_action():
    # Create a new window for changing or adjusting settings
    settings_window = tk.Toplevel(root)  # Create a new Toplevel window
    settings_window.title("Settings")
    settings_window.geometry("500x400")

    # Add a label to the settings window
    tk.Label(settings_window, text="Settings Menu", font=("Helvetica", 16)).pack(pady=20)

    # Add a "Reset Data" button to the settings window
    tk.Button(settings_window, text="Reset Data", font=("Helvetica", 14), command=reset_data).pack(pady=20)

    
def activate_potion(potion_number):
    global till_luck_exp, previous_roll, item_inevntory, lucky_potion_used
    if potion_number == 0: # Collect potions
        previous_roll = 10
        if previous_roll < 10:
            print('not able to collect potions yet!')
        else:
           roll_items()
           previous_roll = 0
    if potion_number == 1: # Lucky potion
        if item_inventory["lucky potion"] >= 1:
            print('lucky potion activated for 25 rolls!')
            till_luck_exp += 25
            item_inventory['lucky potion'] -= 1
            lucky_potion_used += 1
            print(item_inventory['lucky potion'])
        else:
            print('you have no lucky potions left to use!')
    
    
def button_items():
    global item_inventory, previous_rolls, rolls
    # Create a new window for changing or adjusting settings
    items_window = tk.Toplevel(root)  # Create a new Toplevel window
    items_window.title("items and potions")
    items_window.geometry("500x400")
    
    collect_potions = tk.Button(
        items_window,
        text="Collect potions", 
        font=("Helvetica", 14), 
        command=lambda: activate_potion(0)   # Use lambda to pass the argument
    )
    collect_potions.pack(pady=10)
    
    try:
        if item_inventory["lucky potion"] >= 1:
            lucky_potion = tk.Button(
                items_window,
                text="Use lucky potion", 
                font=("Helvetica", 14), 
                command=lambda: activate_potion(1)   # Use lambda to pass the argument
            )
            lucky_potion.pack(pady=10)
    except KeyError:
        pass


async def auto():
    global roll_cooldown, auto_active, rolls, timer_1

    if not auto_active:
        auto_active = True
    else:
        auto_active = False

    while auto_active:
        await asyncio.sleep(roll_cooldown)  # Non-blocking delay
        roll_aura()  # Call your rolling function (replace with actual functionality)
        print("Rolling aura...")  # Debug message (replace with actual functionality)



    



# CUTSCENE (4 POINT STAR)

# Function to draw the window glow effect
def draw_window_glow(surface, color, intensity):
    global WIDTH, HEIGHT
    glow_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for i in range(intensity):
        alpha = int(255 * (1 - i / intensity))
        glow_color = (color[0], color[1], color[2], alpha)
        pygame.draw.rect(glow_surface, glow_color, (i, i, WIDTH - 2 * i, HEIGHT - 2 * i), 1)
    surface.blit(glow_surface, (0, 0))

    
def bezier_point(p0, p1, p2, t):
    """Calculate the Bezier curve point for parameter t."""
    x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0]
    y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1]
    return x, y
 

# DRAW THE CURVED STAR
# Function to calculate Bezier curve points
def bezier_point(p1, control, p2, t):
    x = (1 - t) ** 2 * p1[0] + 2 * (1 - t) * t * control[0] + t ** 2 * p2[0]
    y = (1 - t) ** 2 * p1[1] + 2 * (1 - t) * t * control[1] + t ** 2 * p2[1]
    return x, y

# Function to draw a curved star with dynamic resizing and glow effects
def draw_curved_star(surface, center, outer_radius, inner_radius, angle, fill_color, glow_intensity=0):
    points = []
    num_points = 8  # Total number of points (outer + inner)

    # Calculate the main points of the star
    for i in range(num_points):
        if i % 2 == 0:  # Outer points (north, south, east, west)
            radius = outer_radius
        else:  # Inner points (subpoints, shorter)
            radius = inner_radius * 0.8  # Adjust this multiplier for shorter subpoints
        theta = angle + (i * math.pi / 4)  # 8 points, spaced evenly
        x = center[0] + radius * math.cos(theta)
        y = center[1] + radius * math.sin(theta)
        points.append((x, y))

    # Generate inward-curved segments
    filled_star_points = []
    for i in range(len(points)):
        p1 = points[i]  # Current point
        p2 = points[(i + 1) % len(points)]  # Next point
        mid_x = (p1[0] + p2[0]) / 2  # Midpoint between p1 and p2
        mid_y = (p1[1] + p2[1]) / 2

        # Control point for inward curve (shifted towards the center)
        control_x = (mid_x + center[0]) / 2
        control_y = (mid_y + center[1]) / 2

        # Generate curve points
        for t in range(21):  # Generate points along the curve (0 to 1 in steps)
            t /= 20  # Normalize t to 0-1
            filled_star_points.append(bezier_point(p1, (control_x, control_y), p2, t))

    # Fill the star
    pygame.draw.polygon(surface, fill_color, filled_star_points)

    # Add glow effect if intensity is provided
    if glow_intensity > 0:
        draw_window_glow(surface, fill_color, glow_intensity)

# Function to animate the star cutscene
def animate_star(spins, colour):
    global screen
    clock = pygame.time.Clock()
    angle = 0
    outer_radius = 75  # Starting size
    inner_radius = 30  # Starting size for inner points
    min_outer_radius = 50  # Minimum size threshold
    glow_intensity = 0  # Initial glow intensity
    max_outer_radius = 100  # Target size for the growth phase
    glow_threshold = 0.9 * max_outer_radius  # When to start increasing glow
    glow_max_intensity = 200  # Maximum glow intensity

    # Phase 1: Shrink the star
    while outer_radius > min_outer_radius:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill((0, 0, 0))
        draw_curved_star(screen, (WIDTH // 2, HEIGHT // 2), outer_radius, inner_radius, angle, colour)
        pygame.display.flip()

        # Gradually decrease size
        outer_radius -= 1
        inner_radius = outer_radius * 0.4  # Keep inner radius proportional

        # Keep the star spinning
        angle += 0.05
        if angle >= 2 * math.pi:
            angle -= 2 * math.pi

        clock.tick(60)

    # Phase 2: Hold at minimum size for 3 seconds
    hold_time = 2 * 60  # 3 seconds at 60 FPS
    while hold_time > 0:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill((0, 0, 0))
        draw_curved_star(screen, (WIDTH // 2, HEIGHT // 2), min_outer_radius, min_outer_radius * 0.4, angle, colour)
        pygame.display.flip()

        # Keep the star spinning
        angle += 0.05
        if angle >= 2 * math.pi:
            angle -= 2 * math.pi

        hold_time -= 1
        clock.tick(60)

    # Phase 3: Grow the star and gradually show the glow
    while outer_radius < max_outer_radius:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill((0, 0, 0))
        draw_curved_star(screen, (WIDTH // 2, HEIGHT // 2), outer_radius, inner_radius, angle, colour, glow_intensity)

        pygame.display.flip()

        # Gradually increase size
        outer_radius += 1
        inner_radius = outer_radius * 0.4  # Keep inner radius proportional

        # Increase glow intensity as the star approaches its maximum size
        if outer_radius >= glow_threshold:
            glow_intensity = min(glow_max_intensity, int((outer_radius - glow_threshold) / (max_outer_radius - glow_threshold) * glow_max_intensity))

        # Keep the star spinning
        angle += 0.05
        if angle >= 2 * math.pi:
            angle -= 2 * math.pi

        clock.tick(60)

    # Phase 4: Hold at full glow for 2 seconds
    hold_glow_time = 0.5 * 60  # 2 seconds at 60 FPS
    while hold_glow_time > 0:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill((0, 0, 0))
        draw_curved_star(screen, (WIDTH // 2, HEIGHT // 2), max_outer_radius, max_outer_radius * 0.4, angle, colour, glow_intensity)
        pygame.display.flip()

        # Keep the star spinning
        angle += 0.05
        if angle >= 2 * math.pi:
            angle -= 2 * math.pi

        hold_glow_time -= 1
        clock.tick(60)

    # Phase 5: Gradually decrease the glow
    while glow_intensity > 0:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill((0, 0, 0))
        draw_curved_star(screen, (WIDTH // 2, HEIGHT // 2), max_outer_radius, max_outer_radius * 0.4, angle, colour, glow_intensity)

        pygame.display.flip()

        # Gradually decrease glow intensity
        glow_intensity -= 5

        # Keep the star spinning
        angle += 0.05
        if angle >= 2 * math.pi:
            angle -= 2 * math.pi

        clock.tick(60)



# Function to handle the point cutscene
def point_cutscene(colour_c):
    global WIDTH, HEIGHT, screen

    # Ensure Pygame is initialized
    if not pygame.get_init():
        pygame.init()

    # Switch to fullscreen mode
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    pygame.display.set_caption("Star Animation Cutscene")

    # Run the animation
    animate_star(spins=5, colour=colour_c)

    # After animation, quit the display but keep Pygame initialized
    pygame.display.quit()  # Close the display but leave Pygame running

def start_asyncio_loop():
    """Ensure the asyncio loop is running alongside Tkinter."""
    try:
        # Check for an existing running loop
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # No loop is running; create and set a new one
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    def run_loop():
        # Run the event loop without blocking
        loop.call_soon(loop.stop)
        loop.run_forever()
        root.after(50, run_loop)

    root.after(50, run_loop)


    
# GUI Setup
root = tk.Tk()
root.title("RNG Game")
root.geometry("800x600")

rolls_label = tk.Label(root, text=f"Rolls: {rolls}", font=("Helvetica", 16))
rolls_label.pack(pady=20)

result_label = tk.Label(root, text="Press \'roll\' button to start rolling!", font=("Helvetica", 16))
result_label.pack(pady=20)

# Create sections (Frames)
left_frame = tk.Frame(root)
center_frame = tk.Frame(root)
right_frame = tk.Frame(root)

# Place frames using `pack` (left, center, right alignment)
left_frame.pack(side="left", padx=20, pady=20, fill="y")
center_frame.pack(side="left", padx=20, pady=20, fill="y")
right_frame.pack(side="left", padx=20, pady=20, fill="y")


roll_button = tk.Button(left_frame, text=f"Roll Aura {bonus_roll_label}", font=("Helvetica", 14), command=button_1_action)
roll_button.pack(pady=10)

item_button = tk.Button(left_frame, text=f"Items and Potions", font=("Helvetica", 14), command=button_items)
item_button.pack(pady=10)

auto_button = tk.Button(
    left_frame, 
    text="Auto Roll (Roll button is disabled)", 
    font=("Helvetica", 14), 
    command=lambda: asyncio.create_task(auto())  # Correctly pass the coroutine to create_task
)
auto_button.pack(pady=10)

tk.Button(left_frame, text="View Inventory", font=("Helvetica", 14), command=button_2_action).pack(pady=10)
tk.Button(left_frame, text="Craft Gears", font=("Helvetica", 14), command=button_3_action).pack(pady=10)
tk.Button(left_frame, text="View Quests", font=("Helvetica", 14), command=button_4_action).pack(pady=10)
tk.Button(left_frame, text="Settings", font=("Helvetica", 14), command=button_5_action).pack(pady=10)


pygame.display.quit()  # Close the Pygame display

# Start the asyncio event loop
start_asyncio_loop()

# Start the Tkinter main loop
root.mainloop()
