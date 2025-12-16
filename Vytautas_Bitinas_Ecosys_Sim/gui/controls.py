import tkinter as tk
from tkinter import ttk
from code.config import WorldConfig


class Controls(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.grid(padx=10, pady=10)
        self._make_widgets()

    def _make_widgets(self):
        row = 0
        defaults = WorldConfig()

        def add_label_entry(label, default, varname):
            nonlocal row
            ttk.Label(self, text=label).grid(column=0, row=row, sticky="w")
            ent = ttk.Entry(self, width=12)
            ent.insert(0, str(default))
            ent.grid(column=1, row=row)
            setattr(self, varname, ent)
            row += 1

        add_label_entry("Initial energy", defaults.prey_initial_energy, "e_prey_energy")
        add_label_entry("Prey move cost", defaults.prey_base_move_cost, "e_prey_move")
        add_label_entry("Prey eat amount", defaults.prey_eat_amount, "e_prey_eat")
        add_label_entry("Prey reproduce thresh", defaults.prey_base_reproduce_threshold, "e_prey_rep")

        ttk.Separator(self, orient="horizontal").grid(column=0, row=row, columnspan=2, sticky="ew", pady=6)
        row += 1

        add_label_entry("Initial energy", defaults.predator_initial_energy, "e_pred_energy")
        add_label_entry("Pred move cost", defaults.predator_base_move_cost, "e_pred_move")
        add_label_entry("Pred eat gain", defaults.predator_eat_gain, "e_pred_gain")
        add_label_entry("Pred reproduce thresh", defaults.predator_base_reproduce_threshold, "e_pred_rep")

        ttk.Separator(self, orient="horizontal").grid(column=0, row=row, columnspan=2, sticky="ew", pady=6)
        row += 1

        # General world controls
        add_label_entry("Width", defaults.width, "e_width")
        add_label_entry("Height", defaults.height, "e_height")
        add_label_entry("Initial prey", defaults.initial_prey, "e_prey")
        add_label_entry("Initial predators", defaults.initial_predators, "e_pred")
        add_label_entry("Max steps", defaults.max_steps, "e_steps")

        self.animate_var = tk.BooleanVar(value=defaults.animate)
        ttk.Checkbutton(self, text="Animate", variable=self.animate_var).grid(column=0, row=row, columnspan=2, sticky="w")
        row += 1

        btn_frame = ttk.Frame(self)
        btn_frame.grid(column=0, row=row, columnspan=2, pady=(8, 0))
        self.btn_animate = ttk.Button(btn_frame, text="Run (Animate)")
        self.btn_batch = ttk.Button(btn_frame, text="Run (Batch)")
        self.btn_quit = ttk.Button(btn_frame, text="Quit")
        self.btn_animate.pack(side="left", padx=4)
        self.btn_batch.pack(side="left", padx=4)
        self.btn_quit.pack(side="left", padx=4)

    def get_values(self):
        return {
            'prey_initial_energy': float(self.e_prey_energy.get()),
            'prey_base_move_cost': float(self.e_prey_move.get()),
            'prey_eat_amount': float(self.e_prey_eat.get()),
            'prey_base_reproduce_threshold': float(self.e_prey_rep.get()),
            'predator_initial_energy': float(self.e_pred_energy.get()),
            'predator_base_move_cost': float(self.e_pred_move.get()),
            'predator_eat_gain': float(self.e_pred_gain.get()),
            'predator_base_reproduce_threshold': float(self.e_pred_rep.get()),
            'width': int(self.e_width.get()),
            'height': int(self.e_height.get()),
            'initial_prey': int(self.e_prey.get()),
            'initial_predators': int(self.e_pred.get()),
            'max_steps': int(self.e_steps.get()),
            'animate': bool(self.animate_var.get()),
        }
