import os
import subprocess
import tkinter as tk
from tkinter import ttk, colorchooser, filedialog, messagebox
from PIL import Image, ImageDraw, ImageFont
import math

class BZFontGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("BZ Holographic Suite - spritea.sta Version")
        self.root.geometry("750x950")
        
        self.output_dir = tk.StringVar(value=os.path.join(os.getcwd(), "output"))
        self.font_path = tk.StringVar(value="Arial") 
        self.variant_count = tk.IntVar(value=10)
        self.text_color = "#00FF00"
        self.spacing = tk.DoubleVar(value=1.5)
        self.export_mode = tk.StringVar(value="Sheet") 

        self.create_widgets()

    def create_widgets(self):
        tab_control = ttk.Notebook(self.root)
        self.gen_tab = ttk.Frame(tab_control)
        self.lua_tab = ttk.Frame(tab_control)
        tab_control.add(self.gen_tab, text='1. Asset Generator')
        tab_control.add(self.lua_tab, text='2. Lua Code Generator')
        tab_control.pack(expand=1, fill="both")

        gen_frame = ttk.Frame(self.gen_tab, padding="20")
        gen_frame.pack(fill="both", expand=True)

        # Mode Selection
        mode_frame = ttk.LabelFrame(gen_frame, text=" Export Strategy ", padding=10)
        mode_frame.pack(fill="x", pady=(0, 15))
        ttk.Radiobutton(mode_frame, text="Individual DDS (Master Material)", variable=self.export_mode, value="Individual").pack(side="left", padx=10)
        ttk.Radiobutton(mode_frame, text="Sprite Sheet (spritea.sta)", variable=self.export_mode, value="Sheet").pack(side="left", padx=10)

        ttk.Label(gen_frame, text="Output Directory:").pack(anchor="w")
        path_frame = ttk.Frame(gen_frame)
        path_frame.pack(fill="x", pady=(0, 10))
        ttk.Entry(path_frame, textvariable=self.output_dir).pack(side="left", fill="x", expand=True)
        ttk.Button(path_frame, text="Browse", command=self.browse_output).pack(side="right")

        ttk.Label(gen_frame, text="Font File (.ttf):").pack(anchor="w")
        font_frame = ttk.Frame(gen_frame)
        font_frame.pack(fill="x", pady=(0, 10))
        ttk.Entry(font_frame, textvariable=self.font_path).pack(side="left", fill="x", expand=True)
        ttk.Button(font_frame, text="Load Font", command=self.browse_font).pack(side="right")

        ttk.Label(gen_frame, text="Variants per Character:").pack(anchor="w")
        ttk.Spinbox(gen_frame, from_=1, to=20, textvariable=self.variant_count).pack(fill="x", pady=5)

        ttk.Button(gen_frame, text="Select Color", command=self.choose_color).pack(pady=10)
        self.color_preview = tk.Frame(gen_frame, height=25, bg=self.text_color, relief="sunken", borderwidth=1)
        self.color_preview.pack(fill="x", pady=(0, 20))

        ttk.Button(gen_frame, text="BUILD ASSETS", command=self.generate, style="Accent.TButton", cursor="hand2").pack(fill="x", ipady=15)

        # Lua Tab
        lua_frame = ttk.Frame(self.lua_tab, padding="20")
        lua_frame.pack(fill="both", expand=True)
        ttk.Label(lua_frame, text="Handle Name:").pack(anchor="w")
        self.handle_name = ttk.Entry(lua_frame); self.handle_name.insert(0, "h"); self.handle_name.pack(fill="x")
        ttk.Label(lua_frame, text="Text String:").pack(anchor="w", pady=(10,0))
        self.lua_input = ttk.Entry(lua_frame); self.lua_input.insert(0, "Grizzly One"); self.lua_input.pack(fill="x")
        self.lua_output = tk.Text(lua_frame, height=20, font=("Consolas", 10), bg="#1e1e1e", fg="#d4d4d4", padx=10, pady=10)
        self.lua_output.pack(fill="both", expand=True, pady=10)
        ttk.Button(lua_frame, text="Generate Lua", command=self.generate_lua_block).pack(pady=5)

    def get_ascii_map(self):
        return {32:"sp", 33:"ex", 34:"qu", 35:"ha", 36:"dl", 37:"pc", 38:"am", 39:"ap", 40:"lp", 41:"rp", 42:"as", 43:"pl", 44:"cm", 45:"da", 46:"dt", 47:"sl", 58:"cl", 59:"sc", 60:"lt", 61:"eq", 62:"gt", 63:"qm", 64:"at", 91:"lb", 92:"bs", 93:"rb", 94:"cr", 95:"un", 96:"gr", 123:"lc", 124:"pi", 125:"rc", 126:"ti"}

    def browse_output(self):
        p = filedialog.askdirectory(); self.output_dir.set(p) if p else None
    def browse_font(self):
        p = filedialog.askopenfilename(filetypes=[("Fonts", "*.ttf *.otf")]); self.font_path.set(p) if p else None
    def choose_color(self):
        c = colorchooser.askcolor()[1]
        if c: self.text_color = c; self.color_preview.config(bg=c)

    def get_auto_font(self, target_px):
        try:
            fpath = self.font_path.get() if os.path.exists(self.font_path.get()) else "arial.ttf"
            test_size = 10
            font = ImageFont.truetype(fpath, test_size)
            bbox = font.getbbox("W")
            scale = target_px / max(bbox[2]-bbox[0], bbox[3]-bbox[1])
            return ImageFont.truetype(fpath, int(test_size * scale))
        except: return ImageFont.load_default()

    def generate(self):
        out = self.output_dir.get()
        if not os.path.exists(out): os.makedirs(out)
        
        # Defining characters list at the start of the method
        chars = []
        for i in range(65, 91): chars.append((f"ui{chr(i)}", chr(i)))
        for i in range(97, 123): chars.append((f"uiL{chr(i).upper()}", chr(i)))
        for i in range(48, 58): chars.append((f"ui{chr(i)}", chr(i)))
        for code, name in self.get_ascii_map().items(): chars.append((f"ui_{name}", chr(code)))

        mode = self.export_mode.get()
        
        with open(os.path.join(out, "master_font.material"), "w") as mf:
            mf.write('import * from "sprites.material"\n\n')
            if mode == "Sheet":
                self.build_sheet(chars, out, mf)
            else:
                self.build_individual(chars, out, mf)

        tconv = os.path.join(os.getcwd(), "texconv.exe")
        if os.path.exists(tconv):
            subprocess.run([tconv, "-f", "BC3_UNORM", "-y", "-o", out, os.path.join(out, "*.png")], creationflags=subprocess.CREATE_NO_WINDOW)
            for f in os.listdir(out):
                if f.endswith(".png"): os.remove(os.path.join(out, f))
        
        messagebox.showinfo("Success", f"Build finished in {mode} mode.")

    def build_sheet(self, chars, out, mf, cell=96):
        sheet_dim = 1024
        cols = 10 
        sheet = Image.new("RGBA", (sheet_dim, sheet_dim), (0, 0, 0, 0))
        draw = ImageDraw.Draw(sheet)
        fnt = self.get_auto_font(cell - 6)
        sta_lines = ["# BZ Optimized Sprite Sheet", "# HARDCODED TO spritea.sta"]

        # Material points to the DDS we are about to make
        mf.write('material font_sheet : BZSprite/Additive\n{\n\tset_texture_alias DiffuseMap font_sheet.dds\n}\n')

        for idx, (base, char) in enumerate(chars):
            x, y = (idx % cols) * cell, (idx // cols) * cell
            bbox = draw.textbbox((0, 0), char, font=fnt)
            draw.text((x + (cell-(bbox[2]-bbox[0]))/2, y + (cell-(bbox[3]-bbox[1]))/2 - bbox[1]), char, font=fnt, fill=self.text_color)
            
            for i in range(1, self.variant_count.get() + 1):
                vn = f"{base}{i}"
                # Registry entries in spritea.sta
                sta_lines.append(f'"{vn}" font_sheet {x} {y} {cell} {cell} {sheet_dim} {sheet_dim} 0x00000000')
                self.write_odf(out, vn, vn) 

        sheet.save(os.path.join(out, "font_sheet.png"))
        with open(os.path.join(out, "spritea.sta"), "w") as f: f.write("\n".join(sta_lines))

    def build_individual(self, chars, out, mf):
        fnt = self.get_auto_font(60)
        for base, char in chars:
            img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            bbox = draw.textbbox((0, 0), char, font=fnt)
            draw.text(((64-(bbox[2]-bbox[0]))/2, (64-(bbox[3]-bbox[1]))/2 - bbox[1]), char, font=fnt, fill=self.text_color)
            img.save(os.path.join(out, f"{base}.png"))

            for i in range(1, self.variant_count.get() + 1):
                vn = f"{base}{i}"
                self.write_odf(out, vn, f"{vn}.tga")
                mf.write(f'material {vn}.tga : BZSprite/Additive\n{{\n\tset_texture_alias DiffuseMap {base}.dds\n}}\n\n')

    def write_odf(self, out, name, tex):
        with open(os.path.join(out, f"{name}.odf"), "w") as f:
            f.write(f'[ExplosionClass]\nclassLabel="explosion"\nparticleTypes=1\nparticleClass1="{name}.l"\nparticleCount1=1\n\n[l]\nrenderBase="draw_sprite"\nsimulateBase="sim_null"\ntextureName="{tex}"\nstartColor="255 255 255 255"\nfinishColor="255 255 255 255"\nstartRadius=1.2\nfinishRadius=1.2\nanimateTime=1e30\nlifeTime=0.5\n')

    def generate_lua_block(self):
        text = self.lua_input.get(); h = self.handle_name.get(); s = self.spacing.get(); usage = {}; map = self.get_ascii_map()
        lua = [f"-- Generated for: {text}", f"local p = GetPosition({h})", f"local r = GetRight({h})", f"local u = GetUp({h})"]
        start_offset = -((len(text)-1)*s / 2)
        for i, char in enumerate(text):
            if char == " ": continue
            if 'A' <= char <= 'Z': b = f"ui{char}"
            elif 'a' <= char <= 'z': b = f"uiL{char.upper()}"
            elif '0' <= char <= '9': b = f"ui{char}"
            else: b = f"ui_{map.get(ord(char), 'un')}"
            usage[b] = usage.get(b, 0) + 1
            off = start_offset + (i * s)
            lua.append(f'MakeExplosion("{b}{usage[b]}", p + (r * {off:.2f}) + (u * 2.5))')
        self.lua_output.delete(1.0, tk.END); self.lua_output.insert(tk.END, "\n".join(lua))

if __name__ == "__main__":
    root = tk.Tk(); app = BZFontGenerator(root); root.mainloop()
