from tkinter import *
from glob import glob
import pandas as pd
import data_handler
from tkinter import messagebox
from idlelib.tooltip import Hovertip

######################################################################################
# ------------------------------------- Função ------------------------------------- #
######################################################################################

# TODO: std_standard_code não está presente no script
# TODO: nova regra para coluna parent_sample_number
# TODO: alterar sufixos da coluna column_name para "_LAB"
# TODO: adicionar 2 segundos para cada novo registro na coluna date_imported
# TODO: copiar métodos do cabeçalho para gerar os dados da coluna analytical_technique
# TODO: nova regra para coluna module_name
# TODO: popular a coluna laboratory_name com os registros da coluna Laboratory da tabela de entrada
# TODO: popular a coluna lab_assay_uofm com os registros da coluna unit_of_measure


def btn_execute():
    folder_path = tbx_table.get("1.0", "end-1c")
    input_files_list = [f.replace('\\', '/') for f in glob(f"{folder_path}/*.xlsx")]
    sheet = tbx_sheet.get("1.0", "end-1c")
    cols = ["A,B,C,F:" + col for col in tbx_lastcol.get("1.0", "end-1c").split(sep=',')]
    output_files_list = [f[:-5] + '_SCD.csv' for f in input_files_list]

    index = ["Holeid", "parent_sample_number",
             "Sample number", "Dispatch",
             "Assay sample type", "Lab",
             "lab_reference_number", "analysis_date"]

    rename = {"Holeid": "hole_number",
              "Sample number": "sample_number",
              "Assay sample type": "sample_type",
              "Dispatch": "dispatch_number"}

    col_order = ['hole_number', 'sample_number', 'std_standard_code', 'lab_reference_number',
                 'analysis_date', 'dispatch_number', 'column_name', 'original_result',
                 'math_performed', 'action_reason', 'original_element', 'date_imported',
                 'imported_by', 'original_result_number', 'result_after_math', 'unit_of_measure',
                 'analytical_technique', 'sample_type', 'lab_element', 'module_name', 'laboratory_id',
                 'laboratory_name', 'parent_sample_number', 'lab_method_code', 'lab_assay_uofm']


    if folder_path == '' or sheet == '' or cols == '':
        messagebox.showerror('Erro', "Por favor, preencha todos os campos!")
    elif len(input_files_list) == 0:
        messagebox.showerror('Erro', f"Não há arquivos .xlsx na pasta {folder_path}.")
    elif len(input_files_list) != len(cols):
        messagebox.showerror('Erro', f"O número de últimas colunas ({len(cols)}) não é igual ao número de arquivos ({len(input_files_list)}) na pasta {folder_path}.")
    else:
        for in_f, c, out_f in zip(input_files_list, cols, output_files_list):
            df = pd.read_excel(in_f, sheet_name=sheet, header=0, usecols=c)
            stacked = data_handler.stack_data_frame(df, index, rename)
            data_handler.column_name_manipulation(stacked)
            df_out = stacked[col_order]
            df_out.to_csv(out_f, index=False, encoding='cp1252')
        messagebox.showinfo('Script Concluído', f'Arquivos gerados com sucesso na pasta {folder_path}.')


######################################################################################
# ------------------------------------ Interface ----------------------------------- #
######################################################################################

# Criação da janela principal
root = Tk()

# Ícone
root.wm_iconbitmap('datamine.ico')
# Título
root.title("Datamine GDMS")
# Dimensões da tabela
root.geometry("310x210")
# Configuração de background
root.configure(background='white')

# Widgets
txt_title = Label(root, text="Geração Sample Column Details", bg='white', fg='black', font="lucida 12 bold")
txt_table = Label(root, text="Diretório das Tabelas:", bg='white', fg='black', justify=LEFT, anchor='w', padx=10)
tbx_table = Text(root, height=1, width=20, bg='light yellow')
txt_sheet = Label(root, text="Nome da Aba:", bg='white', fg='black', justify=LEFT, anchor='w', padx=10)
tbx_sheet = Text(root, height=1, width=20, bg='light yellow')
txt_lastcol = Label(root, text="Últimas Colunas:", bg='white', fg='black', justify=LEFT, anchor='w', padx=10)
tbx_lastcol = Text(root, height=1, width=20, bg='light yellow')
btn_exec = Button(root, text="Executar", width=15, command=lambda: btn_execute())
txt_version = Label(root, text="v0.0.1", bg='white', fg='black', justify=RIGHT, anchor='e')

# Associando widgets à janela principal
txt_title.grid(row=0, column=0, columnspan=2, pady=10)
txt_table.grid(row=1, column=0, pady=5, sticky=W)
tbx_table.grid(row=1, column=1)
txt_sheet.grid(row=2, column=0, pady=5, sticky=W)
tbx_sheet.grid(row=2, column=1)
txt_lastcol.grid(row=3, column=0, pady=5, sticky=W)
tbx_lastcol.grid(row=3, column=1)
btn_exec.grid(row=4, column=0, columnspan=2, pady=10)
txt_version.grid(row=5, column=1, sticky=E)

# Tooltips
tip_table = Hovertip(tbx_table, "Caminho para a pasta \nque contém as tabelas \nde entrada.")
tip_sheet = Hovertip(tbx_sheet, "Nome da aba dos arquivos Excel. \nPor padrão, adota-se 'sample'.")
tip_lastcols = Hovertip(tbx_lastcol, "Nomes das últimas colunas \nseparados por vírgula. \nExemplo: AT,R,AV,AV,AS.")

# Execução do app
root.mainloop()
