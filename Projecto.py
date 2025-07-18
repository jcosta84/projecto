import customtkinter as ctk
from tkinter import filedialog, messagebox
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import json, os
from urllib.parse import quote_plus


#------------------- Configuração conxeção a base de dados -----------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(BASE_DIR, 'config', 'config.json')

with open(config_path, 'r') as f:
    config = json.load(f)

server = config["BD_SERVER"]
database = config["BD_NAME"]
user = config["BD_USER"]
password = config["BD_PASSWORD"]
driver = config["BD_DRIVER"]

driver_enconded = quote_plus(driver)

engine = create_engine(
    f"mssql+pyodbc://{user}:{password}@{server}/{database}?driver={driver_enconded}",
    fast_executemany=True
)

base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

#------------------- frame de facturação ---------------------------------------------------------
class FacturaFrame(ctk.CTkFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        ctk.CTkLabel(self, text="Departamento de Facturação", font=("Arial", 20)).pack(pady=10)

        self.menu_selector = ctk.CTkSegmentedButton(
            self,
            values=["Importação", "Dashboard", "Analise Maturidade"],
            command=self.mudar_secao
        )
        self.menu_selector.pack(pady=20)
        self.menu_selector.set("Importação")

        self.secao_frame = ctk.CTkFrame(self)
        self.secao_frame.pack(fill="both", expand=True)

        # Criação dos botões uma única vez
        self.import_button = ctk.CTkButton(
            self.secao_frame,
            text="Importação Script Fact",
            command=self.importar_factura
        )
        self.save_button = ctk.CTkButton(
            self.secao_frame,
            text="Guardar na Base de Dados",
            command=self.guardar_na_base,
            state="disabled"
        )

        # Inicializa a secao
        self.mudar_secao("Importação")

        self.fact = None  # Inicializa variável para os dados importados

    def mudar_secao(self, opcao):
        # Esconde todos os widgets do frame
        for widget in self.secao_frame.winfo_children():
            widget.pack_forget()

        if opcao == "Importação":
            self.import_button.pack(pady=10)
            self.save_button.pack(pady=10)

        elif opcao == "Dashboard":
            label = ctk.CTkLabel(self.secao_frame, text="Dashboard será aqui.")
            label.pack(pady=10)

        elif opcao == "Analise Maturidade":
            label = ctk.CTkLabel(self.secao_frame, text="Análise de Maturidade será aqui.")
            label.pack(pady=10)

    def importar_factura(self):
        file_path = filedialog.askopenfile(filetypes=[("Text Files", "*.txt")])
        if file_path:
            try:
                colunas = ['BOA IND', 'EMP ID', 'UC', 'Prod', 'DT_PROC', 'DT_FACT', 'NR_FACT', 'CLI_ID', 'CLI_CONTA', 'CLI', 'TP_FACT', 'TP_CLI',
                'COD_TARIFA', 'VAL_TOT', 'CONCEITO', 'QTDE', 'VALOR']
                self.fact = pd.read_csv(file_path, sep="\t", names=colunas)

                # Conversões de tipo
                self.fact['UC'] = self.fact['UC'].astype(int)
                self.fact['TP_FACT'] = pd.to_numeric(self.fact['TP_FACT'], errors='coerce')
                self.fact['TP_CLI'] = self.fact['TP_CLI'].astype(str)
                self.fact['COD_TARIFA'] = self.fact['COD_TARIFA'].astype(str)
                self.fact['Prod'] = self.fact['Prod'].astype(str)

                #tabela Unidade
                dados = [['10201000', 'Praia'],
                        ['10202000', 'São Domingos'],
                        ['10203000', 'Santa Catarina'],
                        ['10204000', 'Tarrafal'],
                        ['10205000', 'Calheta'],
                        ['10206000', 'Santa Cruz'],
                        ['10701000', 'Mosteiros'],
                        ['10702000', 'São Filipe'],
                        ['10801000', 'Maio'],
                        ['10901000', 'Brava'],
                        ['10101000', 'Mindelo'],
                        ['10301000', 'SAL'],
                        ['10401000', 'BOAVISTA'],
                        ['10501000', 'VILA DA RIBEIRA BRAVA'],
                        ['10601000', 'R.GRANDE - N.S.Rosário'],
                        ['10602000', 'PORTO NOVO - S.João Baptista'],
                        ['10603000', 'PAUL - S.António das Pombas'],
                        ['10502000', 'Tarrafal S.Nicolau'],
                        ['10000000', 'Electra SUL']
                        ]
                unidade = pd.DataFrame(dados, columns=['UC', 'Unidade'])
                unidade['UC'] = unidade['UC'].astype(int)
                unidade.set_index('UC', inplace=True)

                #tabela Produto
                dados2 = [['EB', 'Baixa Tensão'],
                        ['EE', 'Baixa Tensão Especial'],
                        ['EM', 'Media Tensão'],
                        ['AG', 'Agua']
                        ]
                produto = pd.DataFrame(dados2, columns=['Prod', 'Produto'])
                produto.set_index('Prod', inplace=True)

                #tabela Tipo Factura
                dados3 = [['11', 'Em Ciclo Leitura'],
                        ['12', 'Em Ciclo Estimativa'],
                        ['22', 'Baixa Voluntária'],
                        ['23', 'Baixa por Dívida'],
                        ['24', 'Alterações Contratuais'],
                        ['28', 'Baixa Forçada'],
                        ['29', 'Substit. Modif.'],
                        ['30', 'Substituição'],
                        ['33', 'Acerto de Cobrança'],
                        ['39', 'Facturação Diversa'],
                        ['99', 'Lig Relig CompPg']
                        ]
                tp_fact = pd.DataFrame(dados3, columns=['TP_FACT', 'Tipo_Factura'])
                tp_fact['TP_FACT'] = tp_fact['TP_FACT'].astype(int)
                tp_fact.set_index('TP_FACT', inplace=True)

                #tabela Tipo Cliente
                dados4 = [['72', 'Empresa Publica'],
                        ['82', 'Colectivos'],
                        ['93', 'Industriais'],
                        ['94', 'Construção'],
                        ['73', 'Estado-Patrimonio'],
                        ['91', 'Domésticos'],
                        ['92', 'Comércio, Industria, Agricul.'],
                        ['21', 'Consumos Próprios'],
                        ['31', 'Autarquias'],
                        ['51', 'Instituições'],
                        ['71', 'Estado-Tesouro'],
                        ['XX', 'Clientes Senhas de Água'],
                        ]
                tip_client = pd.DataFrame(dados4, columns=['TP_CLI', 'Tipo_Cliente'])
                tip_client['TP_CLI'] = tip_client['TP_CLI'].astype(str)
                tip_client.set_index('TP_CLI', inplace=True)

                #tabela Tarifa
                dados5 = [['A1', 'Tarifa Água I'],
                            ['A2', 'Tarifa Água II'],
                            ['A3', 'Tarifa Água III B'],
                            ['A4', 'Tarifa Água III A'],
                            ['A5', 'Tarifa Água II (Turismo)'],
                            ['AD', 'ADA'],
                            ['AP', 'Água Praia'],
                            ['B4', 'Autotanques II'],
                            ['CD', 'Central Dessalinizadora'],
                            ['CP', 'Consumos Proprios'],
                            ['R4', 'Autotanques I (Social)'],
                            ['SA', 'Senhas de Água'],
                            ['XX', 'Venda de Água Avulso'],
                            ['AV', 'Avença'],
                            ['CE', 'Caixa de Escada'],
                            ['D1', 'Tarifa D'],
                            ['D11', 'Tarifa D'],
                            ['D2', 'Tarifa D-S. Nicolau'],
                            ['D3', 'Tarifa D-Social-S. Nicolau'],
                            ['D4', 'Tarifa D - Maio'],
                            ['D5', 'Tarifa D - Social - Maio'],
                            ['DS', 'Tarifa D - Social'],
                            ['IP', 'Iluminação Publica'],
                            ['LM', 'Ligação Provisória - MONO'],
                            ['LP', 'Ligação Provisória'],
                            ['LT', 'Ligação Provisória - TRI'],
                            ['LU', 'Ligação Provisória - MONO URG'],
                            ['S1', 'Tarifa Social'],
                            ['SF', 'Semáfores'],
                            ['T1', 'Trabalhador Electra-S. Nicolau'],
                            ['T2', 'Trab. Electra Is.RTC-S.Nicolau'],
                            ['T3', 'Trabalhador Electra - Maio'],
                            ['T4', 'Trab. Electra Is. RTC - Maio'],
                            ['TB', 'Trabalhador Electra'],
                            ['TI', 'Trab. Electra Isento RTC'],
                            ['TU', 'Ligação Provisória - TRI URG'],
                            ['AV', 'Tarifa Avença'],
                            ['E1', 'Tarifa BTE 1'],
                            ['E2', 'Tarifa BTE'],
                            ['M1', 'Tarifa MT 1'],
                            ['M2', 'Tarifa MT'],
                            ['M3', 'Tarifa MT'],
                            ['TBP', 'Trabalhador Partilhado'],
                            ['TBB', 'Trab. Beneficiário']
                        ]
                tarifa = pd.DataFrame(dados5, columns=['COD_TARIFA', 'Tarifa'])
                tarifa['COD_TARIFA'] = tarifa['COD_TARIFA'].astype(str)
                tarifa = tarifa[~tarifa.index.duplicated(keep='first')]

                #região
                dados9 = [['Praia', 'SUL'],
                        ['São Domingos', 'SUL'],
                        ['Santa Catarina', 'SUL'],
                        ['Tarrafal', 'SUL'],
                        ['Calheta', 'SUL'],
                        ['Santa Cruz', 'SUL'],
                        ['Mosteiros', 'SUL'],
                        ['São Filipe', 'SUL'],
                        ['Maio', 'SUL'],
                        ['Brava', 'SUL'],
                        ['Mindelo', 'NORTE'],
                        ['SAL', 'NORTE'],
                        ['BOAVISTA', 'NORTE'],
                        ['VILA DA RIBEIRA BRAVA', 'NORTE'],
                        ['R.GRANDE - N.S.Rosário', 'NORTE'],
                        ['PORTO NOVO - S.João Baptista', 'NORTE'],
                        ['PAUL - S.António das Pombas', 'NORTE'],
                        ['Tarrafal S.Nicolau', 'NORTE']
                        ]
                regiao = pd.DataFrame(dados9, columns=['Unidade', 'Regiao'])
                regiao.set_index('Unidade', inplace=True)

                # Merge com tabelas auxiliares
                self.fact = self.fact.merge(unidade, on='UC', how='left')
                self.fact = self.fact.merge(produto, on='Prod', how='left')
                self.fact = self.fact.merge(tp_fact, on='TP_FACT', how='left')
                self.fact = self.fact.merge(tip_client, on='TP_CLI', how='left')
                self.fact = self.fact.merge(tarifa, on='COD_TARIFA', how='left')
                self.fact = self.fact.merge(regiao, on='Unidade', how='left')

                #ordenar colunas
                colunas_desejadas = ['Regiao', 'Unidade', 'CIL', 'CLI_ID', 'CLI_CONTA', 'Tipo_Cliente', 'Produto', 'Tipo_Factura',
                     'NR_FACT', 'DT_PROC', 'DT_FACT', 'Tarifa', 'VAL_TOT', 'CONCEITO', 'QTDE', 'VALOR']
                colunas_existentes = [col for col in colunas_desejadas if col in self.fact.columns]
                self.fact = self.fact[colunas_existentes]
                self.fact = self.fact.reset_index(drop=True)

                print(self.fact)
                self.save_button.configure(state="normal")  # habilita o botão salvar
                messagebox.showinfo("Importado", f"{len(self.fact)} linhas importadas e processadas com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao importar/processar: {e}")
                self.save_button.configure(state="disabled")
                self.fact = None

    def guardar_na_base(self):
        try:
            if self.fact is not None:
                self.fact.to_sql('facturas', con=engine, if_exists='append', index=False)
                messagebox.showinfo("Sucesso", "Dados guardados na base de dados com sucesso!")
            else:
                messagebox.showwarning("Aviso", "Nenhum dado para guardar. Importe um arquivo primeiro.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao guardar na base: {e}")

#------------------- Aplicação Principal ----------------------------------------------------------
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Facturação")
        self.geometry("800x600")

        self.factura_frame = FacturaFrame(self)
        self.factura_frame.pack(fill="both", expand=True)

#------------------- Executar -----------------------------------------------------------------------
if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    app = App()
    app.mainloop()
