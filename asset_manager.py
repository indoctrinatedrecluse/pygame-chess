import os
import pygame

# Mapping of piece names to their corresponding Unicode characters
# White pieces
UNICODE_PIECES = {
    'wk': '\u2654', 'wq': '\u2655', 'wr': '\u2656', 
    'wb': '\u2657', 'wn': '\u2658', 'wp': '\u2659',
    # Black pieces
    'bk': '\u265A', 'bq': '\u265B', 'br': '\u265C', 
    'bb': '\u265D', 'bn': '\u265E', 'bp': '\u265F'
}

def create_assets():
    """Generates piece images locally using Unicode characters and Pygame."""
    assets_dir = os.path.join(os.path.dirname(__file__), 'assets', 'pieces')
    os.makedirs(assets_dir, exist_ok=True)
    
    print(f"Generating chess piece assets to {assets_dir}...")

    # We need a hidden pygame display to render fonts
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.init()
    pygame.display.set_mode((1, 1))
    
    # Try to find a font that supports chess symbols. 'segoe ui symbol', 'arial unicode ms', etc.
    # We use a large size so it scales down well
    font_size = 120
    
    # Fallback fonts commonly found on Windows/Mac/Linux that support chess unicode
    fonts_to_try = ['segoeuisymbol', 'arialunicodems', 'dejavusans', 'freeserif', 'symbola']
    
    selected_font = None
    for f in fonts_to_try:
        if f in pygame.font.get_fonts():
            selected_font = pygame.font.SysFont(f, font_size)
            break
            
    # If no specific font is found, try the default system font (might look a bit basic)
    if not selected_font:
        selected_font = pygame.font.SysFont(None, font_size)

    for name, symbol in UNICODE_PIECES.items():
        file_path = os.path.join(assets_dir, f"{name}.png")
        if not os.path.exists(file_path):
            try:
                # White pieces are usually outlined in Unicode, Black are solid. 
                # Let's render them. White piece color: White text. Black piece color: Black text.
                # Actually, standard unicode handles the hollow/solid part. We just need to render them in standard colors.
                # Wait, \u2654 (White King) is hollow. So rendering it in Black is best so the outline shows.
                color = (0, 0, 0) 
                
                # Render the text onto a surface
                text_surface = selected_font.render(symbol, True, color)
                
                # We want to crop it tightly
                rect = text_surface.get_bounding_rect()
                cropped_surface = text_surface.subsurface(rect)
                
                # Save as PNG
                pygame.image.save(cropped_surface, file_path)
                print(f"Generated {name}.png using font rendering.")
            except Exception as e:
                print(f"Failed to generate {name}.png: {e}")
        else:
            print(f"{name}.png already exists.")
            
    pygame.quit()

if __name__ == "__main__":
    create_assets()
    print("Done!")
