import tkinter as tk
import random
import time
import json
import os
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

class TimesTableTrainer:
    def __init__(self, master):
        self.master = master
        self.master.title("Treinador de Tabuada")
        self.master.configure(bg="#161519")
        self.master.geometry("1000x600")

        self.stats_file = "tabuada_stats.json"
        self.game_data_file = "game_data.json"
        self.stats = self.load_stats()
        self.game_data = self.load_game_data()

        self.start_time = 0
        self.correct = 0
        self.incorrect = 0
        self.total_time = 0
        self.history = []
        self.questions_data = {}  # Armazena dados sobre acertos, erros e tempo por cada questão
        self.questions_asked = []  # Questões que já foram feitas (evitar repetição)
        self.tabuadas_escolhidas = []  # Tabuadas selecionadas pelo usuário
        self.current_question = None  # A questão atual
        self.game_id = None  # ID do jogo atual

        self.create_setup_screen()

    def create_setup_screen(self):
        for widget in self.master.winfo_children():
                widget.destroy()

        label = tk.Label(self.master, text="Selecione as tabuadas para treinar:", fg="white", bg="#161519", font=("Minecraft", 25))
        label.pack(pady=10)

        self.check_vars = {}

            # Criação das checkboxes com fonte personalizada, maior e lado a lado
        for i in [2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13]:
            var = tk.BooleanVar()
            chk = tk.Checkbutton(self.master, text=f"{i}", variable=var, fg="white", bg="#161519", font=("Minecraft", 20), selectcolor="black", activebackground="black", activeforeground="white", justify="center", height=1, width=2)
            chk.pack(side="top", padx=1)  # Organiza lado a lado e adiciona espaço entre as checkboxes
            self.check_vars[i] = var
        start_button = tk.Button(self.master, text="Iniciar", command=self.start_game, font=("Minecraft", 15), bg="grey", fg="white")
        start_button.pack(pady=0, anchor="center")  # Usando anchor para centralizar

        stats_button = tk.Button(self.master, text="Estatísticas", command=self.show_stats, font=("Minecraft", 15), bg="grey", fg="white")
        stats_button.pack(pady=0, anchor="center")  # Usando anchor para centralizar

    def start_game(self):
        self.game_id = str(datetime.now().timestamp())  # Gerar um ID de jogo único
        self.correct = 0
        self.incorrect = 0
        self.total_time = 0
        self.history = []
        self.questions_asked = []  # Limpar as questões já feitas

        # Carregar as tabuadas escolhidas pelo usuário
        self.tabuadas_escolhidas = [k for k, v in self.check_vars.items() if v.get()]
        if not self.tabuadas_escolhidas:
            return

        for widget in self.master.winfo_children():
            widget.destroy()

        self.timer_label = tk.Label(self.master, text="0.00s", fg="white", bg="#161519", font=("Minecraft", 30))
        self.timer_label.pack(pady=10)

        # Exibição da questão
        self.question_label = tk.Label(self.master, text="", font=("Minecraft", 200), fg="white", bg="#161519")
        self.question_label.pack(pady=20)

        # Caixa de entrada para a resposta do usuário
        self.answer_entry = tk.Entry(self.master, font=("Minecraft", 36), bg="#161519", fg="white", justify="center", width=4)  # Largura diminuída
        self.answer_entry.pack(pady=10)
        self.answer_entry.bind("<KeyRelease>", self.check_answer)

        # Exibição do resultado correto ao lado da questão
        self.result_label = tk.Label(self.master, text="", font=("Minecraft", 36), fg="yellow", bg="#161519")
        self.result_label.pack(pady=20)

        self.stop_button = tk.Button(self.master, text="Parar", command=self.create_setup_screen, font=("Minecraft", 14), bg="red", fg="white")
        self.stop_button.pack(pady=10)

        # Gerar a primeira questão
        self.new_question()

    def new_question(self):
        # Se já tiver feito todas as questões, reinicia o processo
        max_questions = len(self.tabuadas_escolhidas) * 12
        if len(self.questions_asked) >= max_questions:
            self.questions_asked = []  # Resetando as questões feitas
            self.history = []  # Resetando o histórico de tentativas

        question_key = self.get_random_question()

        # Desmontando a questão em x e y
        self.x, self.y = map(int, question_key.split('x'))
        
        # Criando duas questões (9x4 e 4x9) e escolhendo uma aleatoriamente
        questions = [
            f"{self.x}x{self.y}",  # Exemplo: 9x4
            f"{self.y}x{self.x}",  # Exemplo: 4x9
        ]
        
        # Escolher uma questão aleatória entre as duas
        question_key = random.choice(questions)

        # Calculando a resposta para a questão escolhida
        self.x, self.y = map(int, question_key.split('x'))
        self.answer = self.x * self.y
        self.question_label.config(text=f"{self.x} × {self.y}", fg="white")
        self.answer_entry.delete(0, tk.END)
        self.answer_entry.focus()
        self.result_label.config(text="")  # Limpar o resultado da resposta
        self.start_time = time.time()  # Início do tempo de resposta
        self.update_timer()

        # Marcar a questão como feita
        self.current_question = question_key
        self.questions_asked.append(question_key)

    def update_timer(self):
        elapsed = time.time() - self.start_time
        if self.timer_label.winfo_exists():
            self.timer_label.config(text=f"{elapsed:.2f}s")
        self.timer_updater = self.master.after(50, self.update_timer)

    def check_answer(self, event):
        value = self.answer_entry.get()

        if value.isdigit() and int(value) == self.answer:
            self.master.after_cancel(self.timer_updater)
            time_taken = time.time() - self.start_time
            self.total_time += time_taken
            self.correct += 1
            self.update_stats(self.current_question, True, time_taken)
            self.flash("green")
        elif len(value) >= len(str(self.answer)):
            self.master.after_cancel(self.timer_updater)
            time_taken = time.time() - self.start_time
            self.incorrect += 1
            self.update_stats(self.current_question, False, time_taken)
            self.answer_entry.delete(0, tk.END)  # Limpa o campo após resposta errada
            self.flash("red")

    def flash(self, color):
        self.question_label.config(fg=color)
        self.master.after(150, lambda: self.show_correct_answer())

    def show_correct_answer(self):
        # Exibindo a resposta correta ao lado da questão
        self.result_label.config(text=f"{self.answer}")
        
        # Resetando a cor do texto da questão após 150ms
        self.master.after(150, lambda: self.question_label.config(fg="white"))
        
        self.master.after(150, lambda: self.next_question())  # A próxima pergunta aparece após 150ms

    def next_question(self):
        # Garantir que a próxima questão será gerada corretamente
        self.new_question()


    def show_tabuada_times(self):
    # Calculando o tempo médio por tabuada
        tabuada_times = {}

        for question_key, data in self.questions_data.items():
            tabuada = int(question_key.split('x')[0])  # Pega o número da tabuada (ex: 2 em "2x3")
            tempos = data["tempos"]
            
            if tempos:  # Se houver tempos para essa questão
                avg_time = np.mean(tempos)
                if tabuada not in tabuada_times:
                    tabuada_times[tabuada] = []
                tabuada_times[tabuada].append(avg_time)
        
        # Calculando o tempo médio de cada tabuada
        tabuada_avg_times = {tabuada: np.mean(times) for tabuada, times in tabuada_times.items()}

        # Encontrar a tabuada com o menor e maior tempo médio
        min_tabuada = min(tabuada_avg_times, key=tabuada_avg_times.get)
        max_tabuada = max(tabuada_avg_times, key=tabuada_avg_times.get)

        # Encontrar os tempos médios
        min_time = tabuada_avg_times[min_tabuada]
        max_time = tabuada_avg_times[max_tabuada]

        # Exibir no Tkinter
        for widget in self.master.winfo_children():
            widget.destroy()

        label = tk.Label(self.master, text="Resultados dos Tempos Médios", fg="white", bg="#161519", font=("Minecraft", 16))
        label.pack(pady=10)

        min_label = tk.Label(self.master, text=f"Tabuada com o menor tempo médio: {min_tabuada} com {min_time:.2f} segundos", fg="white", bg="#161519", font=("Minecraft", 14))
        min_label.pack(pady=10)

        max_label = tk.Label(self.master, text=f"Tabuada com o maior tempo médio: {max_tabuada} com {max_time:.2f} segundos", fg="white", bg="#161519", font=("Minecraft", 14))
        max_label.pack(pady=10)

        back_button = tk.Button(self.master, text="Voltar", command=self.create_setup_screen, font=("Minecraft", 14), bg="gray", fg="white")
        back_button.pack(pady=10)



    def update_stats(self, question_key, correct, time_taken):
        """Atualiza as estatísticas e os tempos das questões."""
        if question_key not in self.questions_data:
            self.questions_data[question_key] = {"acertos": 0, "erros": 0, "tempos": [], "prioridade": 0}

        if correct:
            self.questions_data[question_key]["acertos"] += 1
        else:
            self.questions_data[question_key]["erros"] += 1
        self.questions_data[question_key]["tempos"].append(time_taken)

        # Atualizar prioridade
        if correct:
            self.questions_data[question_key]["prioridade"] = max(0, self.questions_data[question_key]["prioridade"] - 0.1)
        else:
            self.questions_data[question_key]["prioridade"] += 1

        self.history.append({"question": question_key, "tempo": time_taken, "correct": correct})
        self.save_stats()

    def get_random_question(self):
        # Retorna uma questão aleatória com maior prioridade nas que erramos ou demoramos mais
        available_questions = []

        for tabuada in self.tabuadas_escolhidas:
            for i in range(2, 14):
                available_questions.append(f"{tabuada}x{i}")

        # Se todas as questões já foram feitas, reinicia o processo
        max_questions = len(self.tabuadas_escolhidas) * 12
        if len(available_questions) == len(self.questions_asked):
            self.questions_asked = []

        available_questions = [q for q in available_questions if q not in self.questions_asked]

        # Ordena as questões pela prioridade (questões com mais erros ou mais tempo de resposta vão ter maior prioridade)
        available_questions.sort(key=lambda q: self.questions_data.get(q, {}).get("prioridade", 0), reverse=True)

        return available_questions[0]  # Seleciona a questão com a maior prioridade

    def save_stats(self):
        with open(self.stats_file, "w") as f:
            json.dump(self.questions_data, f, indent=2)

    def load_stats(self):
        if os.path.exists(self.stats_file):
            with open(self.stats_file, "r") as f:
                return json.load(f)
        return {}

    def save_game_data(self):
        # Salvar dados do jogo com seu winrate
        game_data = self.load_game_data()
        questions = {}
        for question in self.history:
            questions[question["question"]] = {"correct": question["correct"], "time": question["tempo"]}

        game_data[self.game_id] = {
            "questions": questions,
            "winrate": self.correct / (self.correct + self.incorrect) * 100
        }
        with open(self.game_data_file, "w") as f:
            json.dump(game_data, f, indent=2)

    def load_game_data(self):
        if os.path.exists(self.game_data_file):
            with open(self.game_data_file, "r") as f:
                return json.load(f)
        return {}

    def show_stats(self):
        for widget in self.master.winfo_children():
            widget.destroy()

        label = tk.Label(self.master, text="Escolha uma opção", fg="white", bg="#161519", font=("Minecraft", 16))
        label.pack(pady=10)

        # Botão para ver os tempos médios das tabuadas
        button_times = tk.Button(self.master, text="Ver Tempos Médios das Tabuadas", command=self.show_tabuada_times, font=("Minecraft", 14), bg="gray", fg="white")
        button_times.pack(pady=5)

        # Outros botões para funcionalidades, se necessário
        button_2 = tk.Button(self.master, text="Tabuada 02", command=lambda: self.show_performance_graph(2), font=("Minecraft", 14), bg="gray", fg="white")
        button_2.pack(pady=1)

        button_3 = tk.Button(self.master, text="Tabuada 03", command=lambda: self.show_performance_graph(3), font=("Minecraft", 14), bg="gray", fg="white")
        button_3.pack(pady=1)

        button_4 = tk.Button(self.master, text="Tabuada 04", command=lambda: self.show_performance_graph(4), font=("Minecraft", 14), bg="gray", fg="white")
        button_4.pack(pady=1)

        button_5 = tk.Button(self.master, text="Tabuada 05", command=lambda: self.show_performance_graph(5), font=("Minecraft", 14), bg="gray", fg="white")
        button_5.pack(pady=1)

        button_6 = tk.Button(self.master, text="Tabuada 06", command=lambda: self.show_performance_graph(6), font=("Minecraft", 14), bg="gray", fg="white")
        button_6.pack(pady=1)

        button_7 = tk.Button(self.master, text="Tabuada 07", command=lambda: self.show_performance_graph(7), font=("Minecraft", 14), bg="gray", fg="white")
        button_7.pack(pady=1)

        button_8 = tk.Button(self.master, text="Tabuada 08", command=lambda: self.show_performance_graph(8), font=("Minecraft", 14), bg="gray", fg="white")
        button_8.pack(pady=1)

        button_9 = tk.Button(self.master, text="Tabuada 09", command=lambda: self.show_performance_graph(9), font=("Minecraft", 14), bg="gray", fg="white")
        button_9.pack(pady=1)

        button_10 = tk.Button(self.master, text="Tabuada 10", command=lambda: self.show_performance_graph(10), font=("Minecraft", 14), bg="gray", fg="white")
        button_10.pack(pady=1)
        
        button_11 = tk.Button(self.master, text="Tabuada 11", command=lambda: self.show_performance_graph(11), font=("Minecraft", 14), bg="gray", fg="white")
        button_11.pack(pady=1)

        button_12 = tk.Button(self.master, text="Tabuada 12", command=lambda: self.show_performance_graph(12), font=("Minecraft", 14), bg="gray", fg="white")
        button_12.pack(pady=1)

        button_13 = tk.Button(self.master, text="Tabuada 13", command=lambda: self.show_performance_graph(13), font=("Minecraft", 14), bg="gray", fg="white")
        button_13.pack(pady=1)

        back_button = tk.Button(self.master, text="Voltar", command=self.create_setup_screen, font=("Minecraft", 14), bg="gray", fg="white")
        back_button.pack(pady=10)

    def compare_winrates(self):
        # Mostrar gráficos de winrate por jogo
        game_data = self.load_game_data()
        game_ids = sorted(game_data.keys())

        winrates = []
        for game_id in game_ids:
            game = game_data[game_id]
            total_questions = len(game["questions"])
            correct_answers = sum(1 for q in game["questions"] if game["questions"][q]["correct"])
            winrate = correct_answers / total_questions * 100  # Winrate como % de acertos
            winrates.append((game_id, winrate))

        # Plotar o gráfico
        game_ids_sorted = [item[0] for item in winrates]
        winrates_sorted = [item[1] for item in winrates]

        plt.figure(figsize=(10, 6))
        plt.plot(game_ids_sorted, winrates_sorted, marker="o", color="green")
        plt.xlabel("Jogo")
        plt.ylabel("Winrate (%)")
        plt.title("Comparação de Winrate por Jogo")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def show_performance_graph(self, tabuada):
        # Gráfico de tempo médio para a tabuada específica
        question_keys = [key for key in self.questions_data.keys() if key.startswith(str(tabuada))]
        times = [np.mean(self.questions_data[key]["tempos"]) for key in question_keys]
        questions = [key.replace('x', ' × ') for key in question_keys]

        # Plotar o gráfico
        plt.figure(figsize=(10, 6))
        plt.plot(questions, times, marker="o", color="black", label="Tempo médio (s)")
        plt.xlabel("Questões")
        plt.ylabel("Tempo médio (s)")
        plt.title(f"Desempenho da Tabuada do {tabuada}")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    root = tk.Tk()
    app = TimesTableTrainer(root)
    root.mainloop()