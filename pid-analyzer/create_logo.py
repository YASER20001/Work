"""Generate KBR-AMCDE logo as PNG for sidebar usage."""
from PIL import Image, ImageDraw, ImageFont
import math

# High-res then scale for crispness
W, H = 1240, 240
img = Image.new("RGBA", (W, H), (255, 255, 255, 255))
draw = ImageDraw.Draw(img)

# Colors
NAVY = (0, 58, 112)
BLUE = (0, 91, 172)
LIGHT_BLUE = (74, 144, 217)
GOLD = (232, 181, 0)
DARK = (26, 26, 26)
GREEN = (74, 140, 63)
TEAL = (124, 184, 156)

# ── Globe arcs ──
# Main arc: sweeping from bottom-left upward to upper-right
def draw_arc_points(draw, points, color, width):
    for i in range(len(points) - 1):
        draw.line([points[i], points[i+1]], fill=color, width=width)

# Main globe arc (thick navy arc from bottom-left sweeping up and right)
# Using bezier approximation with many line segments
def bezier_quad(p0, p1, p2, steps=80):
    pts = []
    for i in range(steps + 1):
        t = i / steps
        x = (1-t)**2 * p0[0] + 2*(1-t)*t * p1[0] + t**2 * p2[0]
        y = (1-t)**2 * p0[1] + 2*(1-t)*t * p1[1] + t**2 * p2[1]
        pts.append((x, y))
    return pts

# Main outer arc
pts1 = bezier_quad((36, 200), (28, 50), (160, 16), 100)
pts2 = bezier_quad((160, 16), (210, 4), (224, 55), 50)
main_arc = pts1 + pts2
draw_arc_points(draw, main_arc, NAVY, 11)

# Inner arc
inner_arc = bezier_quad((52, 185), (58, 70), (150, 38), 80)
draw_arc_points(draw, inner_arc, LIGHT_BLUE, 7)

# Horizontal latitude arc
lat_arc = bezier_quad((30, 130), (110, 100), (200, 132), 60)
draw_arc_points(draw, lat_arc, NAVY, 6)

# ── Sunburst ──
sun_cx, sun_cy, sun_r = 76, 22, 11
draw.ellipse([sun_cx-sun_r, sun_cy-sun_r, sun_cx+sun_r, sun_cy+sun_r], fill=GOLD)

# Sun rays
ray_len = 10
ray_gap = 5
for angle_deg in [0, 45, 90, 135, 180, 225, 315]:
    a = math.radians(angle_deg)
    x1 = sun_cx + (sun_r + ray_gap) * math.cos(a)
    y1 = sun_cy - (sun_r + ray_gap) * math.sin(a)
    x2 = sun_cx + (sun_r + ray_gap + ray_len) * math.cos(a)
    y2 = sun_cy - (sun_r + ray_gap + ray_len) * math.sin(a)
    draw.line([(x1, y1), (x2, y2)], fill=GOLD, width=5)

# ── Pixel squares ──
squares = [
    (144, 22, 18, DARK),
    (170, 12, 16, NAVY),
    (192, 28, 14, BLUE),
    (168, 35, 14, GREEN),
    (144, 48, 12, GREEN),
    (210, 16, 12, GOLD),
    (196, 6, 10, TEAL),
]
for (sx, sy, sz, sc) in squares:
    draw.rounded_rectangle([sx, sy, sx+sz, sy+sz], radius=3, fill=sc)

# ── Text ──
# Use the boldest available font
font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
try:
    font_kbr = ImageFont.truetype(font_path, 150)
    font_amcde = ImageFont.truetype(font_path, 140)
except:
    font_kbr = ImageFont.load_default()
    font_amcde = font_kbr

# "KBR" in dark navy
draw.text((230, 52), "KBR", fill=NAVY, font=font_kbr)

# "-AMCDE" in blue
# Get KBR width to position the rest
kbr_bbox = draw.textbbox((230, 52), "KBR", font=font_kbr)
dash_x = kbr_bbox[2] + 2

draw.text((dash_x, 58), "-AMCDE", fill=BLUE, font=font_amcde)

# Crop to content with small padding
bbox = img.getbbox()
if bbox:
    pad = 8
    bbox = (max(0, bbox[0]-pad), max(0, bbox[1]-pad),
            min(W, bbox[2]+pad), min(H, bbox[3]+pad))
    img = img.crop(bbox)

# Save
img.save("/home/user/Work/pid-analyzer/static/images/kbr-amcde-logo.png", "PNG", optimize=True)
print(f"Logo saved: {img.size[0]}x{img.size[1]}")
