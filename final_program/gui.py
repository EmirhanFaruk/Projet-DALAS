import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from data_loader import MODELS, station_to_cluster
from predictor import predict_station

class VelibApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Velib Predictor")
        self.geometry("600x450")

        # Station selection
        tk.Label(self, text="Select station:").pack(pady=5)
        from data_loader import stations_df
        self.station_cb = ttk.Combobox(self, values=list(stations_df["station_code"]))
        self.station_cb.pack(pady=5)
        self.station_cb.current(0)

        # Model selection
        tk.Label(self, text="Select model:").pack(pady=5)
        self.model_cb = ttk.Combobox(self, values=[])
        self.model_cb.pack(pady=5)
        self.update_model_dropdown()
        self.station_cb.bind("<<ComboboxSelected>>", lambda e: self.update_model_dropdown())

        # Date & time pickers
        tk.Label(self, text="Select date (YYYY-MM-DD):").pack(pady=5)
        self.date_entry = tk.Entry(self)
        self.date_entry.pack(pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        tk.Label(self, text="Select time (HH:MM):").pack(pady=5)
        self.time_entry = tk.Entry(self)
        self.time_entry.pack(pady=5)
        self.time_entry.insert(0, datetime.now().strftime("%H:%M"))

        # Predict Now button
        self.predict_now_btn = tk.Button(self, text="Predict Now (current time)", command=self.predict_now)
        self.predict_now_btn.pack(pady=5)

        # Predict button
        self.predict_btn = tk.Button(self, text="Predict at selected time", command=self.run_prediction)
        self.predict_btn.pack(pady=10)

        # Output
        self.output = tk.Text(self, height=10)
        self.output.pack(pady=5)

    def update_model_dropdown(self):
        station_code = self.station_cb.get()
        cluster_id = station_to_cluster[station_code]
        models = MODELS[cluster_id]
        model_display = [
            f"{i}: {m['model_name']} | {'lagged' if m['is_lagged'] else 'not_lagged'} | {'behavior+weather' if m['has_behavior_and_weather'] else 'behavior'}"
            for i, m in enumerate(models)
        ]
        self.model_cb["values"] = model_display
        if model_display:
            self.model_cb.current(0)

    def run_prediction(self):
        station_code = self.station_cb.get()
        cluster_id = station_to_cluster[station_code]
        model_idx = int(self.model_cb.get().split(":")[0])
        model_entry = MODELS[cluster_id][model_idx]

        try:
            when = datetime.fromisoformat(f"{self.date_entry.get()} {self.time_entry.get()}")
        except Exception as e:
            messagebox.showerror("Error", f"Invalid date/time: {e}")
            return

        pred = predict_station(station_code, model_entry, when)
        self.output.insert(tk.END, f"\nPrediction for {station_code} at {when}: {pred:.1f} bikes\n")
        self.output.see(tk.END)

    def predict_now(self):
        now = datetime.now()
        self.date_entry.delete(0, tk.END)
        self.time_entry.delete(0, tk.END)
        self.date_entry.insert(0, now.strftime("%Y-%m-%d"))
        self.time_entry.insert(0, now.strftime("%H:%M"))
        self.run_prediction()
