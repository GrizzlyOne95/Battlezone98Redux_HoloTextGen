import os
import subprocess
import tkinter as tk
from tkinter import ttk, colorchooser, filedialog, messagebox
from PIL import Image, ImageDraw, ImageFont
import math

class BZFontGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("BZ Holographic Text Suite")
        self.root.geometry("750x900")
        
        self.output_dir = tk.StringVar(value=os.path.join(os.getcwd(), "output"))
        self.font_path = tk.StringVar(value="Arial") 
        self.font_size = tk.IntVar(value=48)
        self.variant_count = tk.IntVar(value=10)
        self.text_color = "#00FF00"
        self.spacing = tk.DoubleVar(value=1.5)
        
        self.create_widgets()

    def create_widgets(self):
        tab_control = ttk.Notebook(self.root)
        self.gen_tab = ttk.Frame(tab_control)
        self.lua_tab = ttk.Frame(tab_control)
        tab_control.add(self.gen_tab, text='1. Asset Generator')
        tab_control.add(self.lua_tab, text='2. Lua Code Generator')
        tab_control.pack(expand=1, fill="both")

        # --- GENERATOR UI ---
        gen_frame = ttk.Frame(self.gen_tab, padding="20")
        gen_frame.pack(fill="both", expand=True)

        ttk.Label(gen_frame, text="Output Directory:").pack(anchor="w")
        path_frame = ttk.Frame(gen_frame)
        path_frame.pack(fill="x", pady=(0, 10))
        ttk.Entry(path_frame, textvariable=self.output_dir).pack(side="left", fill="x", expand=True)
        ttk.Button(path_frame, text="Browse", command=self.browse_output).pack(side="right")

        ttk.Label(gen_frame, text="Font (.TTF):").pack(anchor="w")
        font_frame = ttk.Frame(gen_frame)
        font_frame.pack(fill="x", pady=(0, 10))
        ttk.Entry(font_frame, textvariable=self.font_path).pack(side="left", fill="x", expand=True)
        ttk.Button(font_frame, text="Load Font", command=self.browse_font).pack(side="right")

        ttk.Label(gen_frame, text="Variants per Character:").pack(anchor="w")
        ttk.Spinbox(gen_frame, from_=1, to=20, textvariable=self.variant_count).pack(fill="x", pady=5)

        ttk.Button(gen_frame, text="Select Color", command=self.choose_color).pack(pady=5)
        self.color_preview = tk.Frame(gen_frame, height=20, bg=self.text_color)
        self.color_preview.pack(fill="x", pady=(0, 20))

        ttk.Button(gen_frame, text="BUILD SPRITE SHEET & ODFS", command=self.generate, style="Accent.TButton").pack(fill="x", ipady=15)

        # --- LUA UI ---
        lua_frame = ttk.Frame(self.lua_tab, padding="20")
        lua_frame.pack(fill="both", expand=True)
        ttk.Label(lua_frame, text="Source Object Handle:").pack(anchor="w")
        self.handle_name = ttk.Entry(lua_frame); self.handle_name.insert(0, "h"); self.handle_name.pack(fill="x")
        ttk.Label(lua_frame, text="Text to Display:").pack(anchor="w", pady=(10,0))
        self.lua_input = ttk.Entry(lua_frame); self.lua_input.insert(0, "Grizzly One"); self.lua_input.pack(fill="x")
        ttk.Label(lua_frame, text="Letter Spacing (Meters):").pack(anchor="w", pady=(10,0))
        ttk.Entry(lua_frame, textvariable=self.spacing).pack(fill="x")
        ttk.Button(lua_frame, text="GENERATE LUA SNIPPET", command=self.generate_lua_block).pack(pady=10)
        self.lua_output = tk.Text(lua_frame, height=20, font=("Consolas", 10), bg="#1e1e1e", fg="#d4d4d4", padx=10, pady=10)
        self.lua_output.pack(fill="both", expand=True)

    def get_ascii_map(self):
        return {32:"sp", 33:"ex", 34:"qu", 35:"ha", 36:"dl", 37:"pc", 38:"am", 39:"ap", 40:"lp", 41:"rp", 42:"as", 43:"pl", 44:"cm", 45:"da", 46:"dt", 47:"sl", 58:"cl", 59:"sc", 60:"lt", 61:"eq", 62:"gt", 63:"qm", 64:"at", 91:"lb", 92:"bs", 93:"rb", 94:"cr", 95:"un", 96:"gr", 123:"lc", 124:"pi", 125:"rc", 126:"ti"}

    def browse_output(self):
        p = filedialog.askdirectory(); self.output_dir.set(p) if p else None

    def browse_font(self):
        p = filedialog.askopenfilename(filetypes=[("Fonts", "*.ttf *.otf")]); self.font_path.set(p) if p else None

    def choose_color(self):
        c = colorchooser.askcolor()[1]
        if c: self.text_color = c; self.color_preview.config(bg=c)

    def generate_lua_block(self):
        text = self.lua_input.get(); h = self.handle_name.get(); ascii_map = self.get_ascii_map(); s = self.spacing.get(); usage = {}
        lua = [f"-- Auto-generated for text: {text}", f"local pos = GetPosition({h})", f"local rt = GetRight({h})", f"local up = GetUp({h})"]
        total_width = (len(text) - 1) * s; start_offset = -(total_width / 2)
        for i, char in enumerate(text):
            if char == " ": continue
            if 'A' <= char <= 'Z': base = f"ui{char}"
            elif 'a' <= char <= 'z': base = f"uiL{char.upper()}"
            elif '0' <= char <= '9': base = f"ui{char}"
            else: base = f"ui_{ascii_map.get(ord(char), 'un')}"
            usage[base] = usage.get(base, 0) + 1
            odf = f"{base}{usage[base]}"
            offset = start_offset + (i * s)
            lua.append(f'MakeExplosion("{odf}", pos + (rt * {offset:.2f}) + (up * 2.5))')
        self.lua_output.delete(1.0, tk.END); self.lua_output.insert(tk.END, "\n".join(lua))

    def generate(self):
        out = self.output_dir.get()
        if not os.path.exists(out): os.makedirs(out)
        chars = []
        for i in range(65, 91): chars.append((f"ui{chr(i)}", chr(i)))
        for i in range(97, 123): chars.append((f"uiL{chr(i).upper()}", chr(i)))
        for i in range(48, 58): chars.append((f"ui{chr(i)}", chr(i)))
        for code, name in self.get_ascii_map().items(): chars.append((f"ui_{name}", chr(code)))

        # 1. Master Material
        with open(os.path.join(out, "font_sheet.material"), "w") as mf:
            mf.write('import * from "sprites.material"\n\nmaterial font_sheet : BZSprite/Additive\n{\n\tset_texture_alias DiffuseMap font_sheet.dds\n}\n')

        # 2. Texture & STA logic
        char_size, cols, sheet_dim = 64, 16, 1024
        sheet = Image.new("RGBA", (sheet_dim, sheet_dim), (0, 0, 0, 0))
        draw = ImageDraw.Draw(sheet)
        try:
            fnt = ImageFont.truetype(self.font_path.get(), self.font_size.get()) if os.path.exists(self.font_path.get()) else ImageFont.truetype(f"{self.font_path.get()}.ttf", self.font_size.get())
        except: fnt = ImageFont.load_default()

        sta_lines = ["# BZ Sprite Sheet"]
        for idx, (base, char) in enumerate(chars):
            col, row = idx % cols, idx // cols
            x, y = col * char_size, row * char_size
            b = draw.textbbox((0, 0), char, font=fnt)
            draw.text((x + (64-(b[2]-b[0]))/2, y + (64-(b[3]-b[1]))/2 - b[1]), char, font=fnt, fill=self.text_color)
            
            for i in range(1, self.variant_count.get() + 1):
                vn = f"{base}{i}"
                sta_lines.append(f'"{vn}" font_sheet {x} {y} {char_size} {char_size} {sheet_dim} {sheet_dim} 0x00000000')
                
                # CORRECTION: ODF textureName is now "uiA1", matching the STA entry exactly
                with open(os.path.join(out, f"{vn}.odf"), "w") as f:
                    f.write(f'[ExplosionClass]\nclassLabel="explosion"\nparticleTypes=1\nparticleClass1="{vn}.l"\nparticleCount1=1\n\n[l]\nrenderBase="draw_sprite"\nsimulateBase="sim_null"\ntextureName="{vn}"\nstartColor="255 255 255 255"\nfinishColor="255 255 255 255"\nstartRadius=1.2\nfinishRadius=1.2\nanimateTime=1e30\nlifeTime=0.5\n')

        sheet.save(os.path.join(out, "font_sheet.png"))
        with open(os.path.join(out, "font_sheet.sta"), "w") as f:
            f.write("\n".join(sta_lines))

        # 3. DDS Process
        tconv = os.path.join(os.getcwd(), "texconv.exe")
        if os.path.exists(tconv):
            subprocess.run([tconv, "-f", "BC3_UNORM", "-y", "-o", out, os.path.join(out, "*.png")], creationflags=subprocess.CREATE_NO_WINDOW)
            if os.path.exists(os.path.join(out, "font_sheet.png")): os.remove(os.path.join(out, "font_sheet.png"))
        
        messagebox.showinfo("Success", "Build complete with no-extension ODF lookups.")

if __name__ == "__main__":
    root = tk.Tk()
    app = BZFontGenerator(root)
    root.mainloop()