import customtkinter
from tkinter import filedialog

def selecionar_diretorio():
    diretorio = filedialog.askdirectory(title="Selecione o Diretório")
    if diretorio:
        print(f"Diretório selecionado: {diretorio}")
        # Faça algo com o diretório selecionado aqui
        # Exemplo: exibir no label
        label_diretorio.configure(text=f"Diretório: {diretorio}")

# Configuração da janela principal com customtkinter
app = customtkinter.CTk()
app.geometry("400x300")
app.title("Seleção de Diretório")

# Botão para abrir a caixa de diálogo
botao_selecionar = customtkinter.CTkButton(master=app, text="Selecionar Diretório", command=selecionar_diretorio)
botao_selecionar.pack(pady=20)

# Label para exibir o diretório selecionado
label_diretorio = customtkinter.CTkLabel(master=app, text="Diretório: ")
label_diretorio.pack()

app.mainloop()