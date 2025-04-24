from lex_analyze import *
from first import *
from second import *

equ_table = {}

def preprocessAssembly(input_name, output_name, delete_equ=False):
    # Dictionary to store EQU definitions
    equ_definitions = {}
    with open(input_name, encoding='utf-8', mode='r') as input_file:
        # Read the entire text from the input file
        text = input_file.read()
        # Find the index of the first occurrence of 'EQU'
        equ_index = text.upper().find('EQU')
        while equ_index != -1:
            # Find the start and end of the line containing 'EQU'
            equ_start = text.rfind('\n', 0, equ_index)
            equ_end = text.find('\n', equ_index)
            if equ_start == -1:
                equ_start = 0
            # Extract the EQU parameter from the line
            equ_param = text[equ_start:equ_end]
            equ_param = equ_param.split()
            # Store the EQU definition in the dictionary
            equ_definitions[equ_param[0]] = ' '.join(equ_param)
            equ_table[equ_param[0]] = equ_param[2]
            # Replace the EQU definition in the text with a placeholder (or remove it if delete_equ is True)
            text = text[:equ_start] + (f'###E_DEFINITION_{equ_param[0][:-1]}#' if not delete_equ else '') + text[text.find('\n', equ_index):]
            # Find the next occurrence of 'EQU'
            equ_index = text.upper().find('EQU')
            
    # Write the modified text to the output file
    with open(output_name, encoding='utf-8', mode='w') as output_file:
        output_file.write(text)
        
    # Replace the EQU placeholders with the actual EQU definitions
    text = ''
    with open(output_name, encoding='utf-8', mode='r') as input_file:
        text = input_file.read()
        for key in equ_table.keys():
            text = text.replace(key, equ_table[key])
            
        if not delete_equ:
            for key in equ_definitions.keys():
                text = text.replace(f'###E_DEFINITION_{key[:-1]}#', equ_definitions[key])
            
    # Write the final text to the output file
    with open(output_name, encoding='utf-8', mode='w') as output_file:
        output_file.write(text)

def parse_input(file_path, lexemes_tables: list, rows_list: list):
    with open(file_path, encoding='utf-8', mode='r') as input_file:
        # Read the first line from the input file
        row = input_file.readline().strip()
        # Continue reading lines until 'END' is encountered
        while row.strip().upper() != 'END':
            # Add the row to the list of rows
            rows_list.append(row)
            # Extract the lexemes from the row and add them to the lexemes table
            lexemes_table_row = extract_lexemes_table_row(row.upper(), basics.punctuationCharacters)
            lexemes_tables.append(lexemes_table_row)
            # Read the next line
            row = input_file.readline().strip()
        # Add the 'END' row to the lexemes table and the list of rows
        lexemes_table_row = extract_lexemes_table_row('END', basics.punctuationCharacters)
        lexemes_tables.append(lexemes_table_row)
        rows_list.append('END')

if __name__ == '__main__':
    # Initialize lists to store lexemes tables, sentence structures, and rows
    lexemes_tables = []
    sentence_structures_table = []
    row_list = []

    # Preprocess the assembly file
    preprocessAssembly(basics.asmTestFile, basics.asmTestFile + 'p')

    # Parse the preprocessed assembly file
    parse_input(basics.asmTestFile + 'p', lexemes_tables, row_list)
    
    # Initialize temporary lists
    lexemes_temp = []
    row_temp = []
    # Filter out empty lexemes tables
    for i in range(len(lexemes_tables)):
        if lexemes_tables[i] != []:
            lexemes_temp.append(lexemes_tables[i])
            row_temp.append(row_list[i])

    # Update lexemes_tables and row_list with the filtered lists
    lexemes_tables = lexemes_temp
    row_list = row_temp

    # Check if all tables start with an identifier
    if not all_tables_start_with_identifier(lexemes_tables):
        print('ERROR')
        exit()

    # Create the sentence structures table
    for i in range(len(lexemes_tables)):
        sentence_structures_table.append(fetchSentenceStructuresTableRow(lexemes_tables[i]))
    # Find the maximum row length
    max_row_len = len(max(sentence_structures_table, key=len))
    # Extend shorter rows to match the maximum length
    for i in range(len(sentence_structures_table)):
        if len(sentence_structures_table[i]) < max_row_len:
            sentence_structures_table[i].extend([0]*(max_row_len - len(sentence_structures_table[i])))

    # Write the lexemes tables and sentence structures table to the output file
    writeLexemesTableAndStructure(basics.resultFile, lexemes_tables, sentence_structures_table, row_list)
    
    # FIRST VIEW
    
    # Preprocess the assembly file and delete macros
    preprocessAssembly(basics.asmTestFile, basics.asmTestFile + 'p', delete_equ=True)
    
    # Reinitialize the lists
    lexemes_tables = []
    sentence_structures_table = []
    row_list = []
    
    # Parse the preprocessed assembly file
    parse_input(basics.asmTestFile + 'p', lexemes_tables, row_list)
    
    # Initialize temporary lists
    lexemes_temp = []
    row_temp = []
    # Filter out empty lexemes tables
    for i in range(len(lexemes_tables)):
        if lexemes_tables[i] != []:
            lexemes_temp.append(lexemes_tables[i])
            row_temp.append(row_list[i])

    # Update lexemes_tables and row_list with the filtered lists
    lexemes_tables = lexemes_temp
    row_list = row_temp
    
    # Check if all tables start with an identifier
    if not all_tables_start_with_identifier(lexemes_tables):
        print('ERROR')
        exit()

    # Create the sentence structures table
    for i in range(len(lexemes_tables)):
        sentence_structures_table.append(fetchSentenceStructuresTableRow(lexemes_tables[i]))
    # Find the maximum row length
    max_row_len = len(max(sentence_structures_table, key=len))
    # Extend shorter rows to match the maximum length
    for i in range(len(sentence_structures_table)):
        if len(sentence_structures_table[i]) < max_row_len:
            sentence_structures_table[i].extend([0]*(max_row_len - len(sentence_structures_table[i])))

    # FIRST VIEW
    # Print the first view and get the variables offsets
    vars_offsets = printFirstView(lexemes_tables, sentence_structures_table, row_list)
    
    # SECOND VIEW
    # Modify the second view using the variables offsets
    modify_second_view(vars_offsets)
    