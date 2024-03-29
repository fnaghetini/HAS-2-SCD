from tkinter import *
from glob import glob
import numpy as np
import pandas as pd
import data_handler
from tkinter import messagebox
from idlelib.tooltip import Hovertip
from data_handler import __select_directory

######################################################################################
# ------------------------------------- Função ------------------------------------- #
######################################################################################


def btn_execute():
    folder_path = __select_directory()
    input_files_list = [f.replace('\\', '/') for f in glob(f"{folder_path}/*.xlsx")]
    cols = ["A:" + col for col in tbx_lastcol.get("1.0", "end-1c").split(sep=',')]

    index = ["Holeid", "sample_number", "parent_sample_number", "dispatch",
             "date_shipped", "Sample Type", "lab_reference_number",
             "Laboratory_ID", "assay date", "std_standard_code"]

    rename = {"Holeid"        : "hole_number",
              "dispatch"      : "dispatch_number",
              "Sample Type"   : "sample_type",
              "Laboratory_ID" : "laboratory_id",
              "assay date"    : "analysis_date"}

    col_order = ['hole_number', 'sample_number', 'std_standard_code', 'lab_reference_number',
                 'analysis_date', 'date_shipped', 'dispatch_number', 'column_name', 'original_result',
                 'math_performed', 'action_reason', 'original_element', 'date_imported',
                 'imported_by', 'original_result_number', 'result_after_math', 'unit_of_measure',
                 'analytical_technique', 'sample_type', 'lab_element', 'module_name', 'laboratory_id',
                 'laboratory_name', 'parent_sample_number', 'lab_method_code', 'lab_assay_uofm']

    if folder_path == '' or cols == '':
        messagebox.showerror('Erro', "Por favor, preencha todos os campos!")
    elif len(input_files_list) == 0:
        messagebox.showerror('Erro', f"Não há arquivos .xlsx na pasta {folder_path}.")
    elif len(input_files_list) != len(cols):
        messagebox.showerror('Erro', f"O número de últimas colunas ({len(cols)}) não é igual ao número de arquivos ({len(input_files_list)}) na pasta {folder_path}.")
    else:
        for in_f, c in zip(input_files_list, cols):
            # Aba sample
            df = pd.read_excel(in_f, sheet_name='sample', header=0, usecols=c)
            # Aba methods
            df_methods = pd.read_excel(in_f, sheet_name='methods', header=0, usecols='A:B', index_col=0)
            dict_methods = df_methods.to_dict(orient='dict')['method']
            # Aba labs
            df_labs = pd.read_excel(in_f, sheet_name='labs', header=0, usecols='A:B', index_col=0)
            dict_labs = df_labs.to_dict(orient='dict')['lab_name']

            stacked = data_handler.stack_data_frame(df, index, rename)
            data_handler.column_name_manipulation(stacked, dict_methods, dict_labs)
            df_out = stacked[col_order]

            if tbx_maxrows.get("1.0", "end-1c") == '':
                nb_chunks = 1
            else:
                max_rows = int(tbx_maxrows.get("1.0", "end-1c"))
                if len(df_out) % max_rows == 0:
                    nb_chunks = len(df_out) // max_rows
                elif len(df_out) <= max_rows:
                    nb_chunks = 1
                else:
                    nb_chunks = (len(df_out) // max_rows) + 1

            for i, chunk in enumerate(np.array_split(df_out, nb_chunks)):
                out_file_name = in_f[:-5] + f'_SCD_pt{str(i+1).zfill(3)}.csv'
                chunk.to_csv(out_file_name, index=False, encoding='utf-8', float_format='%.8f')

        messagebox.showinfo('Script Concluído', f'Arquivo(s) gerado(s) com sucesso na pasta {folder_path}.')


######################################################################################
# ------------------------------------ Interface ----------------------------------- #
######################################################################################

# Criação da janela principal
root = Tk()

# Título
root.title("Datamine GDMS")
# Dimensões da tabela
root.geometry("310x215")
# Configuração de background
root.configure(background='white')

# Widgets
txt_title = Label(root, text="  Geração DHL Sample Column Details", bg='white', fg='black', font="lucida 12 bold", justify=CENTER)
txt_lastcol = Label(root, text="Últimas Colunas:", bg='white', fg='black', justify=LEFT, anchor='w', padx=10)
tbx_lastcol = Text(root, height=1, width=20, bg='light yellow')
txt_maxrows = Label(root, text="Máximo de Linhas:", bg='white', fg='black', justify=LEFT, anchor='w', padx=10)
tbx_maxrows = Text(root, height=1, width=20, bg='white')
btn_exec = Button(root, text="Executar", width=15, cursor='hand2', command=lambda: btn_execute())
txt_version = Label(root, text="v0.0.4", bg='white', fg='black', justify=RIGHT, anchor='e')

# Associando widgets à janela principal
txt_title.grid(row=0, column=0, columnspan=2, pady=20)
txt_lastcol.grid(row=2, column=0, pady=5, sticky=W)
tbx_lastcol.grid(row=2, column=1)
txt_maxrows.grid(row=3, column=0, pady=5, sticky=W)
tbx_maxrows.grid(row=3, column=1)
btn_exec.grid(row=4, column=0, columnspan=2, pady=20)
txt_version.grid(row=5, column=1, sticky=E)

# Tooltips
tip_lastcols = Hovertip(tbx_lastcol, "Nomes das últimas colunas \nseparados por vírgula. \nExemplo: AT,R,AV,AV,AS.")
tip_maxrows = Hovertip(tbx_maxrows, "Número máximo de linhas em um \narquivo. Mantenha em branco para \ngerar um "
                                    "único arquivo.")

# Execução do app
root.mainloop()
