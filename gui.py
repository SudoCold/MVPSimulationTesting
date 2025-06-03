import pygame
import sys
import subprocess
import os
from plot_examples import show_all_plots

def is_running_as_exe():
    """Check if the script is running as a compiled executable"""
    return getattr(sys, 'frozen', False)

def get_executable_path():
    """Get the path to the executable"""
    if is_running_as_exe():
        return sys.executable
    return sys.executable

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def run_simulation():
    """Run the one-piece flow simulation"""
    import one_piece_flow
    one_piece_flow.main()

def run_metrics():
    """Run the process metric viewer"""
    import process_metric_viewer
    process_metric_viewer.main()

def run_main_gui():
    """Run the main GUI"""
    pygame.init()
    screen = pygame.display.set_mode((500, 320))
    pygame.display.set_caption("Manufacturing Visualization & Simulation Launcher")

    font = pygame.font.SysFont('Segoe UI', 22, bold=True)
    title_font = pygame.font.SysFont('Segoe UI', 32, bold=True)
    button_font = pygame.font.SysFont('Segoe UI', 18, bold=True)

    # Industrial/robotic theme colors
    background_top = (80, 90, 110)
    background_bottom = (40, 45, 55)
    button_color = (120, 140, 160)
    button_hover_color = (180, 200, 220)
    button_border = (60, 70, 80)
    text_color = (240, 240, 240)
    accent_yellow = (255, 210, 60)
    accent_orange = (255, 140, 40)

    button_rect = pygame.Rect(60, 160, 380, 44)
    sim_button_rect = pygame.Rect(60, 90, 380, 44)
    metric_button_rect = pygame.Rect(60, 230, 380, 44)

    # Draw a simple robot arm icon
    def draw_robot_arm(surface, x, y, scale=0.7, color=(255,210,60)):
        base_rect = pygame.Rect(x, y+15*scale, 16*scale, 7*scale)
        pygame.draw.rect(surface, (120,120,120), base_rect, border_radius=3)
        pygame.draw.circle(surface, color, (int(x+8*scale), int(y+15*scale)), int(7*scale))
        pygame.draw.line(surface, color, (x+8*scale, y+15*scale), (x+8*scale, y+5*scale), int(5*scale))
        pygame.draw.circle(surface, color, (int(x+8*scale), int(y+5*scale)), int(5*scale))
        pygame.draw.line(surface, (180,180,180), (x+8*scale, y+5*scale), (x+16*scale, y), int(3*scale))
        pygame.draw.circle(surface, (200,200,200), (int(x+16*scale), int(y)), int(3*scale))

    running = True
    while running:
        # Redraw background each frame
        for y in range(screen.get_height()):
            ratio = y / screen.get_height()
            r = int(background_top[0] * (1 - ratio) + background_bottom[0] * ratio)
            g = int(background_top[1] * (1 - ratio) + background_bottom[1] * ratio)
            b = int(background_top[2] * (1 - ratio) + background_bottom[2] * ratio)
            pygame.draw.line(screen, (r, g, b), (0, y), (screen.get_width(), y))

        # Draw title with accent underline
        title_text = title_font.render("Manufacturing Control Panel", True, accent_yellow)
        screen.blit(title_text, (screen.get_width() // 2 - title_text.get_width() // 2, 20))
        pygame.draw.line(screen, accent_orange, (screen.get_width()//2 - 120, 60), (screen.get_width()//2 + 120, 60), 3)

        mouse_pos = pygame.mouse.get_pos()
        plot_color = button_hover_color if button_rect.collidepoint(mouse_pos) else button_color
        sim_color = button_hover_color if sim_button_rect.collidepoint(mouse_pos) else button_color
        metric_color = button_hover_color if metric_button_rect.collidepoint(mouse_pos) else button_color

        # Draw buttons with border and shadow
        for rect, color, icon_color in [
            (button_rect, plot_color, accent_yellow),
            (sim_button_rect, sim_color, accent_orange),
            (metric_button_rect, metric_color, (100, 200, 100))
        ]:
            shadow_rect = rect.move(3, 3)
            pygame.draw.rect(screen, (30, 30, 30), shadow_rect, border_radius=10)
            pygame.draw.rect(screen, color, rect, border_radius=10)
            pygame.draw.rect(screen, button_border, rect, 2, border_radius=10)

        # Draw robot arm icons on buttons
        draw_robot_arm(screen, button_rect.x + 10, button_rect.y + 6, 0.7, accent_yellow)
        draw_robot_arm(screen, sim_button_rect.x + 10, sim_button_rect.y + 6, 0.7, accent_orange)
        # Draw a simple chart icon for the metric button
        mx, my = metric_button_rect.x + 18, metric_button_rect.y + 12
        pygame.draw.rect(screen, (100, 200, 100), (mx, my+16, 6, 14), border_radius=2)
        pygame.draw.rect(screen, (100, 200, 100), (mx+10, my+8, 6, 22), border_radius=2)
        pygame.draw.rect(screen, (100, 200, 100), (mx+20, my+4, 6, 26), border_radius=2)

        # Draw button text
        button_text = button_font.render("Open Plot", True, text_color)
        sim_button_text = button_font.render("One-Piece-Flow Simulation", True, text_color)
        metric_button_text = button_font.render("Sample Process Improvement Metric", True, text_color)
        screen.blit(button_text, (button_rect.x + 50, button_rect.y + (button_rect.height - button_text.get_height()) // 2))
        screen.blit(sim_button_text, (sim_button_rect.x + 50, sim_button_rect.y + (sim_button_rect.height - sim_button_text.get_height()) // 2))
        screen.blit(metric_button_text, (metric_button_rect.x + 50, metric_button_rect.y + (metric_button_rect.height - metric_button_text.get_height()) // 2))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    show_all_plots()
                elif sim_button_rect.collidepoint(event.pos):
                    if is_running_as_exe():
                        subprocess.Popen([get_executable_path(), '--simulation'])
                    else:
                        subprocess.Popen([sys.executable, 'one_piece_flow.py'])
                elif metric_button_rect.collidepoint(event.pos):
                    if is_running_as_exe():
                        subprocess.Popen([get_executable_path(), '--metrics'])
                    else:
                        subprocess.Popen([sys.executable, 'process_metric_viewer.py'])
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == '--simulation':
            run_simulation()
        elif sys.argv[1] == '--metrics':
            run_metrics()
    else:
        run_main_gui() 