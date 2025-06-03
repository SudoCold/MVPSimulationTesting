import pygame
import csv
import os

pygame.init()

WIDTH, HEIGHT = 600, 220
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sample Process Improvement Metric")

font = pygame.font.SysFont('Segoe UI', 16, bold=True)
cell_font = pygame.font.SysFont('Segoe UI', 12)
BG_COLOR = (245, 245, 245)
HEADER_COLOR = (200, 220, 255)
LINE_COLOR = (180, 180, 180)
TEXT_COLOR = (30, 30, 30)

# Sample manufacturing metrics data
rows = [
    ["Metric", "Before", "After", "Improvement"],
    ["Cycle Time (sec)", "45", "15", "66.7%"],
    ["WIP Inventory", "15", "5", "66.7%"],
    ["Lead Time (min)", "11.25", "1.45", "87.1%"],
    ["Quality Rate", "92%", "98%", "6.5%"],
    ["Machine Utilization", "65%", "85%", "30.8%"],
    ["Space Utilization", "1000 sq ft", "400 sq ft", "60%"]
]

# Calculate column widths based on content
col_widths = [max(cell_font.size(str(cell))[0] for cell in col) + 12 for col in zip(*rows)]
table_width = sum(col_widths)
start_x = (WIDTH - table_width) // 2 if table_width < WIDTH else 5
start_y = 40
row_height = 22

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Sample Process Improvement Metric")
    clock = pygame.time.Clock()
    running = True

    while running:
        screen.fill(BG_COLOR)
        # Title
        title = font.render("Sample Process Improvement Metric", True, (40, 60, 120))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 8))
        # Draw table
        y = start_y
        for i, row in enumerate(rows):
            x = start_x
            for j, cell in enumerate(row):
                rect = pygame.Rect(x, y, col_widths[j], row_height)
                color = HEADER_COLOR if i == 0 else BG_COLOR
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, LINE_COLOR, rect, 1)
                text = cell_font.render(str(cell), True, TEXT_COLOR)
                screen.blit(text, (x + 4, y + (row_height - text.get_height()) // 2))
                x += col_widths[j]
            y += row_height
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_pos = pygame.mouse.get_pos()
                    for i, button in enumerate(buttons):
                        if button.collidepoint(mouse_pos):
                            if i == 0:  # Open Plot button
                                show_all_plots()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main() 