from datetime import datetime
from pytz import timezone
import pandas as pd


def stack_data_frame(df, index, rename):
    stacked = df.set_index(index).stack()
    df = stacked.reset_index()
    level_column = "_".join(["level", str(len(index))])
    rename.update({level_column: 'column_name', 0: 'original_result'})
    df.rename(columns=rename, inplace=True)
    return df


def column_name_manipulation(df):
    df['math_performed'] = df.apply(lambda row: __check_min_max(row), axis=1)
    df['action_reason'] = df.apply(lambda row: __check_min_max_reason(row), axis=1)
    df['original_element'] = df.apply(lambda row: __get_original_element(row), axis=1)
    df['date_imported'] = datetime.now(timezone('America/Sao_Paulo'))
    df['imported_by'] = 'Datamine'
    df['original_result_number'] = df.apply(lambda row: __get_original_value(row), axis=1)
    df['result_after_math'] = df.apply(lambda row: __convert_to_original(row), axis=1)
    df['unit_of_measure'] = df.apply(lambda row: __get_unity_measure(row), axis=1)
    df['analytical_technique'] = 'ICPASS'
    df['std_standard_code'] = None
    df['lab_element'] = df['original_element']
    df['module_name'] = df.apply(lambda row: __get_module_name(row), axis=1)
    df['laboratory_id'] = df.apply(lambda row: __make_lab_correspondence(row, 'other'), axis=1)
    df['laboratory_name'] = None
    df['lab_method_code'] = df.apply(lambda row: __get_lab_analytical_method(row), axis=1)
    df['lab_assay_uofm'] = df['unit_of_measure']
    df['column_name'] = df.apply(lambda row: __correct_colum_label(row), axis=1)


def __correct_colum_label(row):
    splitted_column_name = row['column_name'].split('_')
    column_label = splitted_column_name[0] + '_' + splitted_column_name[1] + '_LAB'
    return column_label


def __get_original_element(row):
    column_label = row['column_name']
    element = column_label.split("_")[0]
    return element


def __get_unity_measure(row):
    column_label = row['column_name']
    element = column_label.split("_")[1]
    return element


def __get_unity_measure_lab(row):
    column_label = row['column_name']
    element = column_label.split("_")[1]
    if element == 'ozt':
        return 'ozt'
    return '%'


def __get_module_name(row):
    if pd.isna(row['hole_number']) and row['sample_type'] in ['OR', 'ASSAY']:
        return 'SSTN'
    elif row['sample_type'] in ['STD', 'STANDARD']:
        return 'STD'
    else:
        return 'DHL'


def __make_lab_correspondence(row, field='index'):
    lookup_table = {
        'ALS':(2, 'ALS'),
        'INSP':(12, 'Inspectorate'),
        'NDEF':(23, u'Não Definido'),
        'SGSPE':(26, u'SGS Perú')
    }
    lab = row['Lab']
    if field == 'index':
        return lookup_table.get(lab, (0, lab))[0]
    return lookup_table.get(lab, (0, lab))[1]


def __get_lab_analytical_method(row):
    column_label = row['column_name']
    analytical_method = column_label.split('_')[2]
    return analytical_method


def math_permormance(df):
    df['math_performed'] = df.apply(lambda row: __check_min_max(row), axis=1)
    df['math_reason'] = df.apply(lambda row: __check_min_max_reason(row), axis=1)
    df['original_result_number'] = df.apply(lambda row: __convert_to_original(row), axis=1)
    df['result_after_math'] = df['original_result_number']


def __check_min_max(row):
    if '<' in str(row['original_result']):
        return '/2'
    elif '>' in str(row['original_result']):
        return '*1'


def __check_min_max_reason(row):
    if '<' in str(row['original_result']):
        return 'abaixo LD'
    elif '>' in str(row['original_result']):
        return 'acima LD'


def __get_original_value(row):
    value = row['original_result']
    if '<' in str(value) or '>' in str(value):
        value = str(value)[1:]
    return value


def __convert_to_original(row):    
    value = row['original_result']
    if '<' in str(value):
        value = float(value[1:])/2
    elif '>' in str(value):
        value = float(value[1:])
    return value
