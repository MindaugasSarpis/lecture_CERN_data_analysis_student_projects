#!/usr/bin/env python3
import tkinter as tk
from tkinter import messagebox
from pathlib import Path

from code.config import WorldConfig
from gui.controls import Controls
from gui import runner


def main():
    root = tk.Tk()
    root.title('Ecosystem Simulation Launcher')
    controls = Controls(master=root)

    def on_quit():
        root.destroy()

    def on_run_animate():
        vals = controls.get_values()
        cfg = runner.build_config_from_values(vals)
        if not cfg.animate:
            messagebox.showinfo('Animate disabled', 'Animation is disabled; use Run (Batch) to run non-animated.')
            return
        try:
            runner.run_in_background(cfg, animate=True)
        except Exception as e:
            messagebox.showerror('Run error', str(e))

    def on_run_batch():
        vals = controls.get_values()
        cfg = runner.build_config_from_values(vals)
        cfg.animate = False
        try:
            runner.run_in_background(cfg, animate=False)
        except Exception as e:
            messagebox.showerror('Run error', str(e))

    controls.btn_animate.config(command=on_run_animate)
    controls.btn_batch.config(command=on_run_batch)
    controls.btn_quit.config(command=on_quit)

    root.mainloop()


if __name__ == '__main__':
    main()
