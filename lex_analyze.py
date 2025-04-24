import os

import basics


def display_2d_data(data, file):
    # Calculate the maximum length of each column
    max_lengths = [max([len(str(row[i])) for row in data]) for i in range(len(data[0]))]
    for row in data:
        row_str = ""
        # Format each column in the row
        for i in range(len(row)):
            row_str += "{:<{}}".format(row[i], max_lengths[i] + 2)
        # Print the formatted row to the file
        print(row_str, file=file)

def locate_semicolon(s: str) -> int:
    # Find the position of the semicolon in the string
    semicolon_position = s.find(';')
    if semicolon_position == -1:
        semicolon_position = len(s)
    return semicolon_position

def determineLexemeType(s: str) -> str:
    # Check if the string is a directive
    if s in basics.asmCodeDirectives:
        return 'Ідентифікатор директиви'
    
    # Check if the string is an instruction
    if s in basics.assemblyOpCodes:
        return 'Ідентифікатор мнемокоду машиної інструкції'
    
    # Check if the string is a punctuation character
    if s in basics.punctuationCharacters:
        return 'Односимвольна'
    
    # Check if the string is a register
    if s in basics.registerInfo:
        return basics.registerInfo[s]
    
    # Check if the string is a segment register
    if s in basics.segmentRegistersDescription:
        return basics.segmentRegistersDescription[s]

    # Check if the string is a hexadecimal constant
    if s[0].isdecimal() and s[-1] == 'H':
        is_hex = all(c in '0123456789ABCDEF' for c in s[:-1])
        if is_hex:
            return 'Шістнадцяткова константа'
    
    # Check if the string is a decimal constant
    if s[0].isdecimal():
        if s[-1] == 'D' and s[:-1].isdecimal():
            return 'Десяткова константа'
        elif s.isdecimal():
            return 'Десяткова константа'
    
    # Check if the string is a binary constant
    if s[0].isdecimal() and s[-1] == 'B' and s[:-1].isdecimal():
        return 'Двійкова константа'

    # Check if the string is a valid identifier
    if not s[0].isalpha():
        print('ERROR: Identifier starts with non-alphabetic symbol')
        exit()
        
    if any(c not in basics.identifierCharacterSet for c in s):
        print('ERROR: Identifier contains non-alphabetic symbol')
        exit()

    if len(s) > basics.identifierLengthLimit:
        print('ERROR: Identifier too long')
        exit()

    return 'Ідентифікатор користувача або не визначений'
    
def extract_lexemes_table_row(row: str, CONCAT_LEXEMES: list[str]) -> list:
    # Remove comments from the row
    row = row[:locate_semicolon(row)]
    # Split the row into lexemes
    lexemes = row.split()

    # Split lexemes that contain separators
    for separator in CONCAT_LEXEMES:
        i = 0
        while i < len(lexemes):
            split_lexeme = lexemes[i].split(separator)
            result_lexeme = []

            for e in split_lexeme:
                result_lexeme.extend([e, separator])
            del result_lexeme[-1]

            lexemes = lexemes[:i] + result_lexeme + lexemes[i+1:]
            i += len(result_lexeme)

    # Remove empty lexemes
    lexemes = [x for x in lexemes if x != '']

    # Create the lexeme table
    result_table = []
    for i in range(len(lexemes)):
        result_table.append([i+1, lexemes[i], len(lexemes[i]), determineLexemeType(lexemes[i])])

    return result_table

def getLabelNumber(lexeme_table: list):
    # Iterate over each row in the lexeme table
    for index in range(len(lexeme_table)):
        # Check if the lexeme type is an instruction mnemonic identifier
        if lexeme_table[index][3] == 'Ідентифікатор мнемокоду машиної інструкції':
            return 0
        # Check if the lexeme is a label or directive
        if lexeme_table[index][1] in {':', 'DB', 'DW', 'DD', 'SEGMENT', 'ENDS', 'EQU'}:
            return 1
    # If no label or directive is found, return 0
    return 0

def find_first_instruction(lexeme_table: list):
    # Filter the lexeme table to only include rows where the lexeme type is an instruction mnemonic identifier or a directive identifier
    filtered_table = [row for row in lexeme_table if row[3] == 'Ідентифікатор мнемокоду машиної інструкції' or row[3] == 'Ідентифікатор директиви']
    # If the filtered table is not empty, return the index of the first row
    if len(filtered_table) > 0: 
        return filtered_table[0][0]
    # If the filtered table is empty, return 0
    else:
        return 0

def calculate_instruction_size(lexeme_table: list):
    # Count the number of rows in the lexeme table where the lexeme type is an instruction mnemonic identifier or a directive identifier
    return len([row for row in lexeme_table if row[3] == 'Ідентифікатор мнемокоду машиної інструкції' or row[3] == 'Ідентифікатор директиви'])

def calculateOperandCount(lexeme_table: list):
    # Count the number of rows in the lexeme table where the lexeme is a comma, then add 1 to get the number of operands
    return len([row for row in lexeme_table if row[1] == ',']) + 1

def nextOperand(start_index: int, lexeme_table: list):
    # Iterate over each row in the lexeme table, starting from the given index
    for index in range(start_index, len(lexeme_table)):
        # Check if the lexeme type is an instruction mnemonic identifier, a directive identifier, or a comma
        if lexeme_table[index][3] == 'Ідентифікатор мнемокоду машиної інструкції' \
        or lexeme_table[index][3] == 'Ідентифікатор директиви'\
        or lexeme_table[index][1] == ',':
            # If the next index is within the table, return the index of the next row
            if index+1 < len(lexeme_table):
                return lexeme_table[index+1][0]
            # If the next index is outside the table, return 0
            else:
                return 0
    # If no matching lexeme is found, return 0
    return 0

def calculateOperandSize(start_index: int, lexeme_table: list):
    # If the start index is 0, return 0
    if start_index == 0:
        return 0
    
    operand_size = 0
    # Iterate over each row in the lexeme table, starting from the given index
    while start_index < len(lexeme_table):
        operand_size += 1
        # If the lexeme is a comma, return the current operand size
        if lexeme_table[start_index][1] == ',':
            return operand_size
        start_index += 1
    
    # If no comma is found, return the operand size plus 1
    return operand_size+1

def fetchSentenceStructuresTableRow(lexemes_table: list):
    result_row = []
    # Append the label number, first instruction index, and instruction size to the result row
    result_row.append(getLabelNumber(lexemes_table))
    result_row.append(find_first_instruction(lexemes_table))
    result_row.append(calculate_instruction_size(lexemes_table))

    prev_operand_index = 0
    # For each operand, append the index of the next operand and the size of the operand to the result row
    for _ in range(calculateOperandCount(lexemes_table)):
        result_row.append(nextOperand(prev_operand_index, lexemes_table))
        result_row.append(calculateOperandSize(result_row[-1], lexemes_table))
        prev_operand_index = result_row[3 + _*2]
    
    return result_row

def writeLexemesTableAndStructure(file_path, lexemes_tables: list, sentence_structures_table: list, row_list: list):
    # If the directory does not exist, create it
    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))

    with open(file_path, encoding='utf-8', mode='w') as output_file:
        # structure table titles
        title1_sentence_structures_table = ['Поле міток (імені)', '', 'Поле мнемокоду']
        title2_sentence_structures_table = ['N лексеми поля', 'N першої лексеми поля', 'Кількість лексем поля']
        # For each operand, append the operand titles to the structure table titles
        for i in range((len(sentence_structures_table[0])-3) // 2):
            title1_sentence_structures_table.extend(['', f'{i+1}-й операнд'])
            title2_sentence_structures_table.extend(['N першої лексеми операнда', 'Кількість лексем операнда'])

        # For each lexeme table, print the original row, lexeme table, structure table, and line number
        for i in range(len(lexemes_tables)):
            # original row
            print(f'Рядок програми: "{row_list[i]}"\n', file=output_file)

            # lexemes_table
            print('Таблиця лексем', file=output_file)
            display_2d_data([['N', 'Лексема', 'Довжина', 'Тип']] + lexemes_tables[i], file=output_file)
            print(file=output_file)

            # structure_table
            print('Відповідний рядок таблиці структур', file=output_file)
            display_2d_data([title1_sentence_structures_table, title2_sentence_structures_table] + [sentence_structures_table[i]], file=output_file)

            # line and number
            print('-'*25 + f'{i+1}' + '-'*25 + '\n\n', file=output_file)
            
        # Print the structure table
        display_2d_data([title1_sentence_structures_table, title2_sentence_structures_table] + sentence_structures_table, file=output_file)

def all_tables_start_with_identifier(lexemes_tables: list) -> bool:
    # Check if the first lexeme in each table is an identifier
    for lexeme_table in lexemes_tables:
        if not lexeme_table[0][3].startswith('Ідентифікатор'):
            return False
    return True
