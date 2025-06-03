import pygame
import time
import math
import subprocess
import sys
import os
import csv

pygame.init()
screen = pygame.display.set_mode((700, 320))
pygame.display.set_caption("One-Piece-Flow Simulation")

font = pygame.font.SysFont('Segoe UI', 18, bold=True)
small_font = pygame.font.SysFont('Segoe UI', 14)
label_font = pygame.font.SysFont('Segoe UI', 13, italic=True)

BG_TOP = (60, 80, 160)
BG_BOTTOM = (30, 30, 60)
MATERIAL_COLOR = (255, 220, 120)
MATERIAL_SHADOW = (180, 160, 80)
MACHINE_COLOR = (120, 180, 220)
MACHINE_SHADOW = (80, 120, 180)
FG_COLOR = (180, 220, 120)
FG_SHADOW = (120, 160, 80)
TEXT_COLOR = (255, 255, 255)
BORDER_COLOR = (40, 40, 60)

raw_width = 28
raw_height = 18
raw_gap = 6
raw_count = 5
machine_width = 52
machine_height = 38
machine_gap = 38
num_machines = 3
fg_width = 28
fg_height = 18
fg_gap = 6

# Calculate total width for centering
raw_area_width = 50
fg_area_width = 50
machines_width = num_machines * machine_width + (num_machines - 1) * machine_gap
# Reduce the gap between last machine and finished goods
side_gap = 30
layout_width = raw_area_width + side_gap + machines_width + side_gap + fg_area_width
start_x = (screen.get_width() - layout_width) // 2

raw_start_x = start_x
raw_start_y = 60

machines = []
for i in range(num_machines):
    x = raw_start_x + raw_area_width + side_gap + i * (machine_width + machine_gap)
    y = 110
    machines.append((x, y))

fg_start_x = machines[-1][0] + machine_width + side_gap
fg_start_y = 60

PROCESS_TIME = 15  # seconds

class Material:
    def __init__(self, idx):
        self.idx = idx
        self.stage = 0  # 0=raw, 1=machine1, 2=machine2, 3=machine3, 4=finished
        self.x = raw_start_x
        self.y = raw_start_y + idx * (raw_height + raw_gap)
        self.target_pos = (self.x, self.y)
        self.processing = False
        self.timer = 0

    def move_to(self, x, y):
        self.target_pos = (x, y)
        self.processing = False

    def update(self):
        dx = self.target_pos[0] - self.x
        dy = self.target_pos[1] - self.y
        speed = 4
        if abs(dx) > speed:
            self.x += speed if dx > 0 else -speed
        else:
            self.x = self.target_pos[0]
        if abs(dy) > speed:
            self.y += speed if dy > 0 else -speed
        else:
            self.y = self.target_pos[1]
        if (self.x, self.y) == self.target_pos and self.processing:
            self.timer -= 1/60
            if self.timer < 0:
                self.processing = False
                return True
        return False

materials = [Material(i) for i in range(raw_count)]

machine_slots = [
    {'mat': None, 'timer': 0, 'busy': False},
    {'mat': None, 'timer': 0, 'busy': False},
    {'mat': None, 'timer': 0, 'busy': False},
]
finished_materials = []

clock = pygame.time.Clock()
running = True

def draw_gradient_background(surface, top, bottom):
    for y in range(surface.get_height()):
        ratio = y / surface.get_height()
        r = int(top[0] * (1 - ratio) + bottom[0] * ratio)
        g = int(top[1] * (1 - ratio) + bottom[1] * ratio)
        b = int(top[2] * (1 - ratio) + bottom[2] * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (surface.get_width(), y))

def draw_shadowed_rect(surface, color, shadow, rect, border_radius=0, shadow_offset=2):
    shadow_rect = rect.move(shadow_offset, shadow_offset)
    pygame.draw.rect(surface, shadow, shadow_rect, border_radius=border_radius)
    pygame.draw.rect(surface, color, rect, border_radius=border_radius)
    pygame.draw.rect(surface, BORDER_COLOR, rect, 1, border_radius=border_radius)

def draw_machine_icon(surface, center):
    x, y = center
    pygame.draw.circle(surface, (200, 220, 255), (x, y), 10)
    for i in range(8):
        angle = i * math.pi / 4
        dx = int(14 * math.cos(angle))
        dy = int(14 * math.sin(angle))
        pygame.draw.circle(surface, (120, 180, 220), (x + dx, y + dy), 3)
    pygame.draw.circle(surface, (120, 180, 220), (x, y), 6)
    pygame.draw.circle(surface, (80, 120, 180), (x, y), 3)

def draw_material(surface, x, y, stage):
    # Draw base body
    pygame.draw.rect(surface, MATERIAL_COLOR, (x, y, raw_width, raw_height), border_radius=6)
    pygame.draw.rect(surface, (100, 90, 40), (x, y, raw_width, raw_height), 1, border_radius=6)
    cx = x + raw_width // 2
    cy = y + raw_height // 2
    # Draw arms if stage >= 2 (after machine 1)
    if stage >= 2:
        # Left arm
        pygame.draw.line(surface, (180, 160, 80), (x, y+raw_height//2), (x-8, y+raw_height//2-8), 3)
        # Right arm
        pygame.draw.line(surface, (180, 160, 80), (x+raw_width, y+raw_height//2), (x+raw_width+8, y+raw_height//2-8), 3)
    # Draw legs if stage >= 4 (after machine 3/finished)
    if stage >= 4:
        # Left leg
        pygame.draw.line(surface, (180, 160, 80), (cx-6, y+raw_height), (cx-10, y+raw_height+12), 3)
        # Right leg
        pygame.draw.line(surface, (180, 160, 80), (cx+6, y+raw_height), (cx+10, y+raw_height+12), 3)

def draw_person(surface, x, y):
    pygame.draw.circle(surface, (220, 200, 180), (x, y), 10)
    pygame.draw.rect(surface, (120, 120, 120), (x-7, y+10, 14, 18), border_radius=4)
    pygame.draw.line(surface, (120, 120, 120), (x-7, y+20), (x-18, y+30), 4)
    pygame.draw.line(surface, (120, 120, 120), (x+7, y+20), (x+18, y+30), 4)
    pygame.draw.line(surface, (120, 120, 120), (x-2, y+28), (x-2, y+38), 3)
    pygame.draw.line(surface, (120, 120, 120), (x+2, y+28), (x+2, y+38), 3)

def draw_truck(surface, x, y, load_count):
    pygame.draw.rect(surface, (80, 80, 80), (x, y, 80, 32), border_radius=6)
    pygame.draw.rect(surface, (120, 120, 120), (x+60, y+8, 20, 16), border_radius=4)
    pygame.draw.circle(surface, (40, 40, 40), (x+18, y+32), 8)
    pygame.draw.circle(surface, (40, 40, 40), (x+62, y+32), 8)
    for i in range(load_count):
        draw_material(surface, x+8+i*15, y+6, 0)

def scenario_people_load_truck():
    truck_x, truck_y = 120, 110
    people_xs = [80 + i*50 for i in range(raw_count)]
    product_start_y = 180
    product_end_x = truck_x + 8
    product_end_y = truck_y + 6
    loaded = 0
    for i in range(raw_count):
        for step in range(0, 41):
            screen.fill((200, 220, 255))
            label = font.render("People bring products to the truck (Customer Demand)", True, (40, 40, 40))
            screen.blit(label, (screen.get_width()//2 - label.get_width()//2, 30))
            # Draw people
            for j in range(raw_count):
                draw_person(screen, people_xs[j], product_start_y)
            # Draw truck
            draw_truck(screen, truck_x, truck_y, loaded)
            # Animate product being carried
            px = people_xs[i] + (product_end_x - people_xs[i]) * step // 40
            py = product_start_y + (product_end_y - product_start_y) * step // 40
            draw_material(screen, px, py, 0)
            pygame.display.flip()
            pygame.time.wait(18)
        loaded += 1
    # Show final loaded truck for a moment
    screen.fill((200, 220, 255))
    label = font.render("People bring products to the truck (Customer Demand)", True, (40, 40, 40))
    screen.blit(label, (screen.get_width()//2 - label.get_width()//2, 30))
    for j in range(raw_count):
        draw_person(screen, people_xs[j], product_start_y)
    draw_truck(screen, truck_x, truck_y, loaded)
    pygame.display.flip()
    pygame.time.wait(900)

def scenario_truck_moving_highway():
    road_y = 180
    truck_y = road_y - 40
    plant_x = 540
    plant_y = road_y - 60
    plant_w = 120
    plant_h = 100
    door_w = 32
    door_h = 40
    for tx in range(120, plant_x-40, 3):  # Move truck to plant
        screen.fill((200, 220, 255))
        # Draw highway
        pygame.draw.rect(screen, (80, 80, 80), (0, road_y, screen.get_width(), 40))
        for lx in range(0, screen.get_width(), 40):
            pygame.draw.rect(screen, (255, 255, 100), (lx+10, road_y+18, 20, 4))
        # Draw scenery (simple trees)
        for t in range(0, screen.get_width(), 120):
            pygame.draw.rect(screen, (60, 120, 60), (t+20, road_y-30, 12, 30))
            pygame.draw.circle(screen, (40, 180, 40), (t+26, road_y-30), 16)
        # Draw manufacturing plant
        pygame.draw.rect(screen, (180, 180, 200), (plant_x, plant_y, plant_w, plant_h), border_radius=8)
        pygame.draw.rect(screen, (120, 120, 140), (plant_x, plant_y, plant_w, plant_h), 3, border_radius=8)
        # Draw plant door
        pygame.draw.rect(screen, (100, 100, 120), (plant_x+plant_w//2-door_w//2, plant_y+plant_h-door_h, door_w, door_h), border_radius=4)
        # Draw plant sign
        sign = small_font.render("Manufacturing Plant", True, (40, 40, 60))
        pygame.draw.rect(screen, (255, 255, 210), (plant_x+plant_w//2-54, plant_y-22, 108, 22), border_radius=6)
        screen.blit(sign, (plant_x+plant_w//2-sign.get_width()//2, plant_y-20))
        label = font.render("Truck Delivering to Plant...", True, (40, 40, 40))
        screen.blit(label, (screen.get_width()//2 - label.get_width()//2, 30))
        draw_truck(screen, tx, truck_y, raw_count)
        pygame.display.flip()
        pygame.time.wait(22)
    # Pause with truck at plant
    for _ in range(30):
        screen.fill((200, 220, 255))
        pygame.draw.rect(screen, (80, 80, 80), (0, road_y, screen.get_width(), 40))
        for lx in range(0, screen.get_width(), 40):
            pygame.draw.rect(screen, (255, 255, 100), (lx+10, road_y+18, 20, 4))
        for t in range(0, screen.get_width(), 120):
            pygame.draw.rect(screen, (60, 120, 60), (t+20, road_y-30, 12, 30))
            pygame.draw.circle(screen, (40, 180, 40), (t+26, road_y-30), 16)
        pygame.draw.rect(screen, (180, 180, 200), (plant_x, plant_y, plant_w, plant_h), border_radius=8)
        pygame.draw.rect(screen, (120, 120, 140), (plant_x, plant_y, plant_w, plant_h), 3, border_radius=8)
        pygame.draw.rect(screen, (100, 100, 120), (plant_x+plant_w//2-door_w//2, plant_y+plant_h-door_h, door_w, door_h), border_radius=4)
        pygame.draw.rect(screen, (255, 255, 210), (plant_x+plant_w//2-54, plant_y-22, 108, 22), border_radius=6)
        screen.blit(sign, (plant_x+plant_w//2-sign.get_width()//2, plant_y-20))
        label = font.render("Truck Arrived at Plant", True, (40, 40, 40))
        screen.blit(label, (screen.get_width()//2 - label.get_width()//2, 30))
        draw_truck(screen, plant_x-40, truck_y, raw_count)
        pygame.display.flip()
        pygame.time.wait(22)
    pygame.time.wait(800)

def scenario_unload_truck_to_raw():
    # Use manufacturing simulation background and layout
    truck_x, truck_y = 540-40, 200  # Lower the truck
    people_x = truck_x + 40
    people_y = truck_y + 32
    raw_target_x = raw_start_x + (raw_area_width - raw_width)//2
    raw_target_ys = [raw_start_y + i * (raw_height + raw_gap) for i in range(raw_count)]
    for i in range(raw_count):
        for step in range(0, 41):
            draw_gradient_background(screen, BG_TOP, BG_BOTTOM)
            # Draw manufacturing layout
            area_rect = pygame.Rect(raw_start_x - 10, raw_start_y - 30, raw_area_width, 160)
            pygame.draw.rect(screen, (70, 60, 30), area_rect, border_radius=10)
            pygame.draw.rect(screen, (120, 100, 60), area_rect, 1, border_radius=10)
            raw_label = font.render("Raw Materials", True, TEXT_COLOR)
            screen.blit(raw_label, (raw_start_x + (raw_area_width - raw_label.get_width()) // 2, raw_start_y - 25))
            fg_area_rect = pygame.Rect(fg_start_x - 10, fg_start_y - 30, fg_area_width, 160)
            pygame.draw.rect(screen, (40, 70, 30), fg_area_rect, border_radius=10)
            pygame.draw.rect(screen, (80, 120, 60), fg_area_rect, 1, border_radius=10)
            fg_label = font.render("Finished Goods", True, TEXT_COLOR)
            screen.blit(fg_label, (fg_start_x + (fg_area_width - fg_label.get_width()) // 2, fg_start_y - 25))
            for j in range(i):
                draw_material(screen, raw_target_x, raw_target_ys[j], 0)
            # Draw truck at plant (lowered)
            draw_truck(screen, truck_x, truck_y, raw_count-i)
            # Animate person and product moving to raw area
            px = truck_x + 8 + i*15
            py = truck_y + 6
            person_start_x = px + 10
            person_start_y = py + 30
            carry_x = person_start_x + (raw_target_x - person_start_x) * step // 40
            carry_y = person_start_y + (raw_target_ys[i] - person_start_y) * step // 40
            draw_person(screen, carry_x, carry_y)
            draw_material(screen, carry_x-10, carry_y+10, 0)
            pygame.display.flip()
            pygame.time.wait(18)
    # Show final state for a moment
    draw_gradient_background(screen, BG_TOP, BG_BOTTOM)
    area_rect = pygame.Rect(raw_start_x - 10, raw_start_y - 30, raw_area_width, 160)
    pygame.draw.rect(screen, (70, 60, 30), area_rect, border_radius=10)
    pygame.draw.rect(screen, (120, 100, 60), area_rect, 1, border_radius=10)
    raw_label = font.render("Raw Materials", True, TEXT_COLOR)
    screen.blit(raw_label, (raw_start_x + (raw_area_width - raw_label.get_width()) // 2, raw_start_y - 25))
    fg_area_rect = pygame.Rect(fg_start_x - 10, fg_start_y - 30, fg_area_width, 160)
    pygame.draw.rect(screen, (40, 70, 30), fg_area_rect, border_radius=10)
    pygame.draw.rect(screen, (80, 120, 60), fg_area_rect, 1, border_radius=10)
    fg_label = font.render("Finished Goods", True, TEXT_COLOR)
    screen.blit(fg_label, (fg_start_x + (fg_area_width - fg_label.get_width()) // 2, fg_start_y - 25))
    for j in range(raw_count):
        draw_material(screen, raw_target_x, raw_target_ys[j], 0)
    draw_truck(screen, truck_x, truck_y, 0)
    pygame.display.flip()
    pygame.time.wait(900)

def show_metric_scene():
    # Load CSV
    WIDTH, HEIGHT = 600, 220
    metric_font = pygame.font.SysFont('Segoe UI', 16, bold=True)
    metric_cell_font = pygame.font.SysFont('Segoe UI', 12)
    BG_COLOR = (245, 245, 245)
    HEADER_COLOR = (200, 220, 255)
    LINE_COLOR = (180, 180, 180)
    TEXT_COLOR = (30, 30, 30)
    csv_path = os.path.join(os.path.dirname(__file__), 'Sample Process Improvement Metric - Sheet1.csv')
    rows = []
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            rows.append(row)
    col_widths = [max(metric_cell_font.size(str(cell))[0] for cell in col) + 12 for col in zip(*rows)]
    table_width = sum(col_widths)
    start_x = (WIDTH - table_width) // 2 if table_width < WIDTH else 5
    start_y = 40
    row_height = 22
    running_metric = True
    metric_screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Sample Process Improvement Metric")
    while running_metric:
        metric_screen.fill(BG_COLOR)
        # Title
        title = metric_font.render("Sample Process Improvement Metric", True, (40, 60, 120))
        metric_screen.blit(title, (WIDTH//2 - title.get_width()//2, 8))
        # Draw table
        y = start_y
        for i, row in enumerate(rows):
            x = start_x
            for j, cell in enumerate(row):
                rect = pygame.Rect(x, y, col_widths[j], row_height)
                color = HEADER_COLOR if i == 0 else BG_COLOR
                pygame.draw.rect(metric_screen, color, rect)
                pygame.draw.rect(metric_screen, LINE_COLOR, rect, 1)
                text = metric_cell_font.render(str(cell), True, TEXT_COLOR)
                metric_screen.blit(text, (x + 4, y + (row_height - text.get_height()) // 2))
                x += col_widths[j]
            y += row_height
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running_metric = False
        pygame.display.flip()
    pygame.quit()
    exit()

def main():
    pygame.init()
    screen = pygame.display.set_mode((700, 320))
    pygame.display.set_caption("One-Piece-Flow Simulation")
    clock = pygame.time.Clock()
    running = True

    # --- Initial scenario: loading and truck movement ---
    scenario_people_load_truck()
    scenario_truck_moving_highway()
    scenario_unload_truck_to_raw()

    while running:
        draw_gradient_background(screen, BG_TOP, BG_BOTTOM)

        area_rect = pygame.Rect(raw_start_x - 10, raw_start_y - 30, raw_area_width, 160)
        pygame.draw.rect(screen, (70, 60, 30), area_rect, border_radius=10)
        pygame.draw.rect(screen, (120, 100, 60), area_rect, 1, border_radius=10)
        raw_label = font.render("Raw Materials", True, TEXT_COLOR)
        screen.blit(raw_label, (raw_start_x + (raw_area_width - raw_label.get_width()) // 2, raw_start_y - 25))
        for i, mat in enumerate(materials):
            if mat.stage == 0:
                rect_x = raw_start_x + (raw_area_width - raw_width)//2
                rect_y = raw_start_y + i * (raw_height + raw_gap)
                draw_shadowed_rect(screen, MATERIAL_COLOR, MATERIAL_SHADOW, pygame.Rect(rect_x, rect_y, raw_width, raw_height), border_radius=4)
                draw_material(screen, rect_x, rect_y, mat.stage)

        fg_area_rect = pygame.Rect(fg_start_x - 10, fg_start_y - 30, fg_area_width, 160)
        pygame.draw.rect(screen, (40, 70, 30), fg_area_rect, border_radius=10)
        pygame.draw.rect(screen, (80, 120, 60), fg_area_rect, 1, border_radius=10)
        fg_label = font.render("Finished Goods", True, TEXT_COLOR)
        screen.blit(fg_label, (fg_start_x + (fg_area_width - fg_label.get_width()) // 2, fg_start_y - 25))
        for i, mat in enumerate(finished_materials):
            rect_x = fg_start_x + (fg_area_width - fg_width)//2
            rect_y = fg_start_y + i * (fg_height + fg_gap)
            draw_shadowed_rect(screen, FG_COLOR, FG_SHADOW, pygame.Rect(rect_x, rect_y, fg_width, fg_height), border_radius=4)
            draw_material(screen, rect_x, rect_y, 4)  # Final product: arms and legs

        for idx, (mx, my) in enumerate(machines):
            table_rect = pygame.Rect(mx, my, machine_width, machine_height)
            draw_shadowed_rect(screen, MACHINE_COLOR, MACHINE_SHADOW, table_rect, border_radius=8)
            pygame.draw.rect(screen, MACHINE_SHADOW, (mx+6, my+machine_height, 6, 10), border_radius=2)
            pygame.draw.rect(screen, MACHINE_SHADOW, (mx+machine_width-12, my+machine_height, 6, 10), border_radius=2)
            draw_machine_icon(screen, (mx + machine_width//2, my + machine_height//2))
            label = font.render(f"Machine {idx+1}", True, TEXT_COLOR)
            screen.blit(label, (mx + (machine_width - label.get_width()) // 2, my - 18))
            if machine_slots[idx]['mat'] is not None and machine_slots[idx]['busy']:
                timer_text = small_font.render(f"{int(machine_slots[idx]['timer'])}s", True, (255, 200, 100))
            else:
                timer_text = small_font.render("15 sec", True, TEXT_COLOR)
            screen.blit(timer_text, (mx + (machine_width - timer_text.get_width()) // 2, my + machine_height + 2))

        for mat in materials:
            if mat.stage > 0 and mat.stage < 4:
                draw_material(screen, int(mat.x), int(mat.y), mat.stage)

        if machine_slots[0]['mat'] is None:
            for mat in materials:
                if mat.stage == 0:
                    mx, my = machines[0]
                    mat.move_to(mx + (machine_width-raw_width)//2, my + (machine_height-raw_height)//2)
                    mat.stage = 1
                    machine_slots[0]['mat'] = mat
                    machine_slots[0]['timer'] = PROCESS_TIME
                    machine_slots[0]['busy'] = False
                    break
        for idx in range(3):
            slot = machine_slots[idx]
            if slot['mat'] is not None and not slot['busy']:
                mat = slot['mat']
                if (mat.x, mat.y) == mat.target_pos:
                    slot['busy'] = True
                    mat.processing = True
                    mat.timer = slot['timer']
        for idx in range(3):
            slot = machine_slots[idx]
            if slot['mat'] is not None and slot['busy']:
                mat = slot['mat']
                done = mat.update()
                slot['timer'] = mat.timer if mat.processing else 0
                if done:
                    slot['mat'] = None
                    slot['busy'] = False
                    if idx < 2:
                        mat.stage += 1
                        mx, my = machines[idx+1]
                        mat.move_to(mx + (machine_width-raw_width)//2, my + (machine_height-raw_height)//2)
                        machine_slots[idx+1]['mat'] = mat
                        machine_slots[idx+1]['timer'] = PROCESS_TIME
                        machine_slots[idx+1]['busy'] = False
                    else:
                        mat.stage = 4
                        finished_materials.append(mat)
        for mat in materials:
            if not mat.processing and (mat.x, mat.y) != mat.target_pos:
                mat.update()

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        clock.tick(60)

    # After all materials are in finished goods, launch process_metric_viewer.py as a separate process
    if len(finished_materials) == raw_count:
        pygame.quit()  # Quit pygame first
        if is_running_as_exe():
            subprocess.Popen([get_executable_path(), '--metrics'])
        else:
            subprocess.Popen([sys.executable, 'process_metric_viewer.py'])
        sys.exit()

    pygame.quit()

if __name__ == "__main__":
    main() 

