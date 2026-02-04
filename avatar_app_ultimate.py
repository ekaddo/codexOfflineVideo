import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path

from core.pipeline import AvatarPipeline, PipelineInputs


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("codexOfflineVideo - RealTalk")
        self.geometry("820x640")
        self.resizable(True, True)

        self.pipeline = AvatarPipeline()

        self.avatar_path = tk.StringVar()
        self.voice_path = tk.StringVar()
        self.ref_video_path = tk.StringVar()
        self.engine_choice = tk.StringVar(value="EchoMimic")

        self._build_ui()

    def _build_ui(self):
        pad = 8
        frm = ttk.Frame(self, padding=pad)
        frm.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frm, text="Voice Sample (WAV/MP3)").grid(row=0, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.voice_path, width=80).grid(row=1, column=0, sticky="we")
        ttk.Button(frm, text="Browse", command=self._pick_voice).grid(row=1, column=1, padx=pad)

        ttk.Label(frm, text="Avatar Image (JPG/PNG)").grid(row=2, column=0, sticky="w", pady=(pad, 0))
        ttk.Entry(frm, textvariable=self.avatar_path, width=80).grid(row=3, column=0, sticky="we")
        ttk.Button(frm, text="Browse", command=self._pick_avatar).grid(row=3, column=1, padx=pad)

        ttk.Label(frm, text="Reference Video (Optional)").grid(row=4, column=0, sticky="w", pady=(pad, 0))
        ttk.Entry(frm, textvariable=self.ref_video_path, width=80).grid(row=5, column=0, sticky="we")
        ttk.Button(frm, text="Browse", command=self._pick_ref).grid(row=5, column=1, padx=pad)

        ttk.Label(frm, text="Renderer").grid(row=6, column=0, sticky="w", pady=(pad, 0))
        engine_menu = ttk.OptionMenu(
            frm,
            self.engine_choice,
            "EchoMimic",
            "EchoMimic",
            "LTX-2 (HQ Intro)",
        )
        engine_menu.grid(row=6, column=1, sticky="e", padx=(0, pad))

        ttk.Label(frm, text="Script").grid(row=7, column=0, sticky="w", pady=(pad, 0))
        self.script_box = tk.Text(frm, height=8, wrap=tk.WORD)
        self.script_box.grid(row=8, column=0, columnspan=2, sticky="nsew")

        self.generate_btn = ttk.Button(frm, text="GENERATE VIDEO", command=self._on_generate)
        self.generate_btn.grid(row=9, column=0, sticky="w", pady=(pad, 0))

        self.status = tk.StringVar(value="Idle")
        ttk.Label(frm, textvariable=self.status).grid(row=9, column=1, sticky="e", padx=(0, pad))

        ttk.Label(frm, text="Log").grid(row=10, column=0, sticky="w", pady=(pad, 0))
        self.log_box = tk.Text(frm, height=10, wrap=tk.WORD, state=tk.DISABLED)
        self.log_box.grid(row=11, column=0, columnspan=2, sticky="nsew")

        frm.columnconfigure(0, weight=1)
        frm.rowconfigure(8, weight=1)
        frm.rowconfigure(11, weight=1)

    def _pick_voice(self):
        path = filedialog.askopenfilename(filetypes=[("Audio", "*.wav;*.mp3")])
        if path:
            self.voice_path.set(path)

    def _pick_avatar(self):
        path = filedialog.askopenfilename(filetypes=[("Image", "*.jpg;*.jpeg;*.png")])
        if path:
            self.avatar_path.set(path)

    def _pick_ref(self):
        path = filedialog.askopenfilename(filetypes=[("Video", "*.mp4;*.mov;*.mkv")])
        if path:
            self.ref_video_path.set(path)

    def _log(self, msg: str):
        self.log_box.configure(state=tk.NORMAL)
        self.log_box.insert(tk.END, msg + "\n")
        self.log_box.configure(state=tk.DISABLED)
        self.log_box.see(tk.END)

    def _on_generate(self):
        engine = self.engine_choice.get()
        use_ltx = engine.startswith("LTX-2")

        if not use_ltx:
            if not self.voice_path.get() or not self.avatar_path.get():
                messagebox.showerror(
                    "Missing Inputs", "Please select a voice sample and avatar image."
                )
                return
        else:
            if not self.script_box.get("1.0", tk.END).strip():
                messagebox.showerror("Missing Script", "Please enter a script.")
                return

        script = self.script_box.get("1.0", tk.END).strip()
        if not script:
            messagebox.showerror("Missing Script", "Please enter a script.")
            return

        self.generate_btn.configure(state=tk.DISABLED)
        self.status.set("Generating...")
        self._log("Starting generation...")

        def work():
            try:
                inputs = PipelineInputs(
                    avatar_image=Path(self.avatar_path.get()) if self.avatar_path.get() else None,
                    script_text=script,
                    voice_sample=Path(self.voice_path.get()) if self.voice_path.get() else None,
                    reference_video=Path(self.ref_video_path.get()) if self.ref_video_path.get() else None,
                    engine_override="ltx2" if use_ltx else None,
                )
                outputs = self.pipeline.run(inputs)
                self._log(f"Done: {outputs.video_path}")
                self.status.set("Complete")
            except Exception as exc:
                self._log(f"Error: {exc}")
                self.status.set("Error")
                messagebox.showerror("Generation Failed", str(exc))
            finally:
                self.generate_btn.configure(state=tk.NORMAL)

        threading.Thread(target=work, daemon=True).start()


if __name__ == "__main__":
    app = App()
    app.mainloop()
