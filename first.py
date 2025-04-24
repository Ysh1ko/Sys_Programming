import basics
from lex_analyze import display_2d_data

current_offset = 0
operands = [None, None, None, None]
operand_ovveride = ''
segment_ovveride = ''
address_ovveride = ''
vars_offsets = {}
user_identifiers = {}
to_print = ''
current_segment = ''
segment_table = {'CS': '', 'DS': '', 'SS': '', 'ES': '', 'GS': '', 'FS': ''}
segments_info = {}
error_num = 0

def processIdentifiersAndDirectives(lexemes_tables: list, sentence_structures_table: list):
    global user_identifiers
    # Iterate over all lexemes tables
    for index in range(len(lexemes_tables)):
        # Check if the first element of the sentence structure is 1 and the fourth element of the lexeme is a user identifier
        if sentence_structures_table[index][0] == 1 and lexemes_tables[index][0][3] == 'Ідентифікатор користувача або не визначений':
            # Get all user identifiers from the lexeme
            user_ids = [x[1] for x in lexemes_tables[index] if x[3] == 'Ідентифікатор користувача або не визначений']
            vars_offsets[user_ids[0]] = None # offset will be written later
            directive_value = -1
            # Check if any of the lexemes contain 'DB', 'DW', or 'DD'
            if any('DB' in sublist for sublist in lexemes_tables[index]):
                directive_value = 1
            elif any('DW' in sublist for sublist in lexemes_tables[index]):
                directive_value = 2
            elif any('DD' in sublist for sublist in lexemes_tables[index]):
                directive_value = 4

            # Add the user identifier and its corresponding directive value to the global dictionary
            user_identifiers[user_ids[0]] = directive_value

    # Check if all user identifiers are unique
    user_ids = user_identifiers.keys()
    if len(user_ids) != len(set(user_ids)):
        print('ERROR') # Identifiers are not unique
        exit()

def processDirective(lexeme: list):
    global to_print  
    global current_offset
    global current_segment
    global segments_info
    
    # Check if the lexeme has at least two elements and the second element is 'ENDS'
    if len(lexeme) >= 2 and lexeme[1][1] == 'ENDS':
        # Add the current offset to the segments info dictionary
        segments_info[lexeme[0][1]] = current_offset
        
    # Check if the lexeme has at least two elements and the second element is 'SEGMENT'
    if len(lexeme) >= 2 and lexeme[1][1] == 'SEGMENT':
        # Reset the current offset and set the current segment
        current_offset = 0
        current_segment = lexeme[0][1]
        
        # Update the segment table if 'DS' or 'CS' is empty
        if segment_table['DS'] == '':
            segment_table['DS'] = current_segment
        elif segment_table['CS'] == '':
            segment_table['CS'] = current_segment
        
    # Check if the lexeme has at least two elements
    if len(lexeme) >= 2:
        # Update the vars offsets dictionary
        vars_offsets[lexeme[0][1]] = {'seg': current_segment, 'offset': current_offset}
        # Check the second element of the lexeme and handle immediate conversion accordingly
        if lexeme[1][1] == 'DB':
            num = handleImmediateConversion(lexeme[2:])
            to_print += f'{num:02X}'
            
        if lexeme[1][1] == 'DW':
            num = handleImmediateConversion(lexeme[2:])
            to_print += f'{num:04X}'

        if lexeme[1][1] == 'DD':
            num = handleImmediateConversion(lexeme[2:])
            to_print += f'{num:08X}'

    return 0

def generate_modrm_sib_encoding(lexeme: list, op_num: int, register: str):
    global to_print
    global segment_ovveride
    global operand_ovveride
    global address_ovveride
    
    # Initialize variable to None
    user_variable = None
    # Iterate over lexeme to find user identifier
    for element in lexeme:
        if element[3] == 'Ідентифікатор користувача або не визначений':
            user_variable = element[1]
            break
    
    # If user variable is found, update operands and segment override
    if user_variable is not None:
        operands[op_num] = vars_offsets[user_variable]['offset']
        
        var_seg = vars_offsets[user_variable]['seg']
        if var_seg != segment_table['DS']:
            for key, value in segment_table.items():
                if value == var_seg:
                    segment_ovveride = f'{int(f"001{basics.segmentRegistersAddresses[key][1:]}110", base=2):02X}'
                    break
    else:
        operands[op_num] = 0

    # Initialize mod, reg, rm, scale, index, base, l, r
    mod = ''
    reg = register
    rm = '101' 

    scale = ''
    index = ''
    base = '' 

    left_bracket = -1 
    right_bracket = -1 
    for i in range(len(lexeme)):
        if lexeme[i][1] == '[':
            left_bracket = i
        elif lexeme[i][1] == ']':
            right_bracket = i
            break
        
    # If brackets are found, update mod, rm, tmp_str
    if left_bracket != -1 and right_bracket != -1:
        mod = '10'
        rm = '100'

        tmp_str = ''.join([x[1] for x in lexeme[left_bracket+1:right_bracket]])
        
        flag = 1
        if '+' in tmp_str:
            tmp_str = tmp_str.split('+')
        if '-' in ''.join(tmp_str):
            for i, e in enumerate(tmp_str):
                if '-' in e:
                    flag = -1
                    tmp_str = tmp_str[:i] + tmp_str[i].split('-') + tmp_str[i+1:]

        base_found = False
        if type(tmp_str) == str:
            tmp_str = [tmp_str]
        for e in tmp_str:
            if e in list(basics.addressesRegisters32)[:-2] and not base_found:
                base = basics.addressesRegisters32[e]
                base_found = True
            elif e.isdigit():
                operands[op_num] += int(e) * flag
                pass
            else:
                base_and_scale = e.split('*')
                if len(base_and_scale) == 2:
                    mod = '10'
                    if base_and_scale[0] in ('1', '2', '4', '8') and base_and_scale[1] in basics.addressesRegisters32:
                        scale = base_and_scale[0]
                        index = basics.addressesRegisters32[base_and_scale[1]]
                    elif base_and_scale[1] in ('1', '2', '4', '8') and base_and_scale[0] in basics.addressesRegisters32:
                        scale = base_and_scale[1]
                        index = basics.addressesRegisters32[base_and_scale[0]]
                    scale = int(scale) // 2
                    scale = f'{scale:02b}' if scale != 4 else '11'
                elif len(base_and_scale) == 1:
                    mod = '01'
                    # only base
                    index = basics.addressesRegisters32[base_and_scale[0]]
                    scale = '00'

    # If operand is not None, update it
    if operands[op_num] is not None:
        if operands[op_num] < 0:
            operands[op_num] = f'{(2**7 + 2**6 + 2**5 + 2**4 + 4 - operands[op_num]):08X}r' 
        else:
            operands[op_num] = f'{operands[op_num]:08X}r'

    # Generate modrm_sib_str and convert it to integer
    modrm_sib_str = f'{mod}{reg}{rm}{scale}{index}{base}'
    modrm_sib_int = int(modrm_sib_str, base=2) if modrm_sib_str != '' else 0
    return {'byte': modrm_sib_int, 'var': user_variable}

def generate_segment_register_encoding(lexeme_list: list):
    global segment_ovveride
    
    # Check if the second element of lexeme_list is in segmentRegistersAddresses
    if lexeme_list[1][:2] in basics.segmentRegistersAddresses:
        # If it is, update segment_ovveride
        segment_ovveride = f'{int(f"001{basics.segmentRegistersAddresses[lexeme_list[1]][1:]}110", base=2):02X}'

def handleImmediateConversion(lexeme_list: list) -> int:
    # Initialize base and number_string
    base = 10 
    number_string = ''
    
    # Check if lexeme_list has only one element
    if len(lexeme_list) == 1:
        # Check the last character of the first element of lexeme_list
        if lexeme_list[0][1][-1] == 'H':
            base = 16  
        elif lexeme_list[0][1][-1] == 'B':
            base = 2   
        elif lexeme_list[0][1][-1] == 'D':
            base = 10 
        elif lexeme_list[0][1][-1].isdigit():
            number_string = f'{int(lexeme_list[0][1], base=10):02X}'
            return int(number_string, base=16)
        elif lexeme_list[0][1][-1] == '\'' and lexeme_list[0][1][0] == '\'' or lexeme_list[0][1][-1] == '\"' and lexeme_list[0][1][0] == '\"':
            const = lexeme_list[0][1][1:-1]
            lexeme_list[0][1] = '"Code"' if const == 'CODE' else f'"{const}"'
            for c in lexeme_list[0][1][1:-1]:
                number_string = f'{ord(c):02X}'
            return int(number_string, base=16)
                
        number_string = f'{int(lexeme_list[0][1][:-1], base=base):02X}'
        
        return int(number_string, base=16)
    else:
        # arithmetic expression
        try:
            # Evaluate the arithmetic expression
            number_string = eval(''.join([x[1] for x in lexeme_list]))
            # Round to the nearest integer
            number_string = round(number_string)
            
            # Find the number of bytes
            byte_count = 0
            if 0 <= abs(number_string) <= 2**8 - 1:
                byte_count = 1
            elif 2**8 <= abs(number_string) <= 2**16 - 1:
                byte_count = 4
            elif 2**16 <= abs(number_string) <= 2**32 - 1:
                byte_count = 8
            
            # Convert to hex. If negative, convert to 2's complement
            if number_string < 0:
                number_string = -number_string
                number_string = f'{number_string:0{8*byte_count}b}'
                number_string = ''.join(['0' if x == '1' else '1' for x in number_string])
                number_string = int(number_string, base=2) + 1
                
            number_string = f'{number_string:0{byte_count*2}X}'
            
            return int(number_string, base=16)
        except:
            print('ERROR: wrong arithmetic expression')
            exit()
        
def check_start_with_al(lexeme_list: list) -> bool:
    # Check if the first element of lexeme_list starts with 'AL'
    return lexeme_list[0][1] == 'AL'
   
def is_eax_register(lexeme_list: list) -> bool:
    # Check if the first element of lexeme_list is 'EAX'
    return lexeme_list[0][1] == 'EAX'

def is_immediate_eight_bit(lexeme_list: list) -> bool:
    try:
        # Convert lexeme_list to an integer
        num = handleImmediateConversion(lexeme_list)
        # Check if num is less than or equal to 2**8 - 1
        return num <= 2**8 - 1
    except:
        return False

def is_imm32_range(lexeme_list: list) -> bool:
    try:
        # Convert lexeme_list to an integer
        num = handleImmediateConversion(lexeme_list)
        # Check if num is in the range 2**8 to 2**32 - 1
        return 2**8 <= num <= 2**32 - 1
    except:
        return False

def is_register32(lexeme_list: list) -> bool:
    # Check if the first element of lexeme_list is in addressesRegisters32
    return lexeme_list[0][1] in basics.addressesRegisters32

def is_register_eight(lexeme_list: list) -> bool:
    # Check if the first element of lexeme_list is in addressesRegisters8
    return lexeme_list[0][1] in basics.addressesRegisters8

def is_member(input_list: list) -> bool:
    # Create a new list with the second element of each sublist in input_list
    transformed_list = [x[1] for x in input_list]
    
    # Check if '[' and ']' are in transformed_list and '[' comes before ']'
    return ('[' in transformed_list and ']' in transformed_list
            and transformed_list.index('[') < transformed_list.index(']'))

def has_word_ptr(input_list: list) -> bool:
    global vars_offsets
    # Initialize user_identifier to None
    user_identifier = None
    
    # Iterate over each element in input_list
    for element in input_list:
        # Check if the fourth element of the sublist is 'Ідентифікатор користувача або не визначений'
        if element[3] == 'Ідентифікатор користувача або не визначений':
            # If it is, update user_identifier and break the loop
            user_identifier = element[1]
            break

    # Initialize byte_ptr, word_ptr, and dword_ptr to False
    byte_ptr = False
    word_ptr = False
    dword_ptr = False
    
    # Iterate over the range of the length of input_list - 1
    for i in range(len(input_list)-1):
        # Check if the second element of the i-th sublist is 'BYTE' and the second element of the (i+1)-th sublist is 'PTR'
        if input_list[i][1] == 'BYTE' and input_list[i+1][1] == 'PTR':
            byte_ptr = True
        # Check if the second element of the i-th sublist is 'WORD' and the second element of the (i+1)-th sublist is 'PTR'
        if input_list[i][1] == 'WORD' and input_list[i+1][1] == 'PTR':
            word_ptr = True
        # Check if the second element of the i-th sublist is 'DWORD' and the second element of the (i+1)-th sublist is 'PTR'
        if input_list[i][1] == 'DWORD' and input_list[i+1][1] == 'PTR':
            dword_ptr = True

    # Return True if user_identifier and user_identifiers[user_identifier] is 1 or byte_ptr is True, and word_ptr and dword_ptr are False
    return (((user_identifier and user_identifiers[user_identifier]) == 1 or byte_ptr)
            and not word_ptr 
            and not dword_ptr)

def has_valid_mem32_type(input_list: list) -> bool:
    global vars_offsets
    # Initialize user_identifier to None
    user_identifier = None
    
    # Iterate over each element in input_list
    for element in input_list:
        # Check if the fourth element of the sublist is 'Ідентифікатор користувача або не визначений'
        if element[3] == 'Ідентифікатор користувача або не визначений':
            # If it is, update user_identifier and break the loop
            user_identifier = element[1]
            break

    # Initialize byte_ptr, word_ptr, and dword_ptr to False
    byte_ptr = False
    word_ptr = False
    dword_ptr = False
    
    # Iterate over the range of the length of input_list - 1
    for i in range(len(input_list)-1):
        # Check if the second element of the i-th sublist is 'BYTE' and the second element of the (i+1)-th sublist is 'PTR'
        if input_list[i][1] == 'BYTE' and input_list[i+1][1] == 'PTR':
            byte_ptr = True
        # Check if the second element of the i-th sublist is 'WORD' and the second element of the (i+1)-th sublist is 'PTR'
        if input_list[i][1] == 'WORD' and input_list[i+1][1] == 'PTR':
            word_ptr = True
        # Check if the second element of the i-th sublist is 'DWORD' and the second element of the (i+1)-th sublist is 'PTR'
        if input_list[i][1] == 'DWORD' and input_list[i+1][1] == 'PTR':
            dword_ptr = True

    # Return True if user_identifier and user_identifiers[user_identifier] is 4 or dword_ptr is True, and word_ptr and byte_ptr are False
    return (((user_identifier and user_identifiers[user_identifier]) == 4 or dword_ptr)
            and not word_ptr 
            and not byte_ptr)

def generateOpcode(lexeme: list):
    global vars_offsets
    global operands
    global current_offset
    
    lexeme_name = lexeme[0][1]
    
    if lexeme_name == 'SCASB':
        code_int = int('AE', base=16)
        code_str = f'{code_int:X}'
        return int(f'{code_str}', base=16)
    
    if lexeme_name == 'DEC':
        operand0 = lexeme[1:]
        
        if is_register_eight(operand0):
            code_int = int('FE00', base=16) + int(f'11{1:03b}{basics.addressesRegisters8[operand0[0][1]]}', base=2)
            code_str = f'{code_int:X}'
            return int(f'{code_str}', base=16)
        
        if is_register32(operand0):
            code_int = int('48', base=16) + int(basics.addressesRegisters32[operand0[0][1]], base=2)
            code_str = f'{code_int:X}'
            return int(f'{code_str}', base=16)
        
    if lexeme_name == 'INC':
        operand0 = lexeme[1:]
        
        if (len(operand0) >= 3
            and operand0[0][1] in basics.segmentRegistersAddresses):
            generate_segment_register_encoding(operand0[0])
            operand0 = operand0[2:]
            
        if (len(operand0) >= 3
            and operand0[2][1] in basics.segmentRegistersAddresses):
            generate_segment_register_encoding(operand0[2])
            operand0 = operand0[:2] + operand0[3:]
            
        if has_word_ptr(operand0):
            modrm_sib = generate_modrm_sib_encoding(operand0, 0, f'{0:03b}')
            return int(f'FE{modrm_sib["byte"]:02X}', base=16)
        
        if has_valid_mem32_type(operand0):
            modrm_sib = generate_modrm_sib_encoding(operand0, 0, f'{0:03b}')
            return int(f'FF{modrm_sib["byte"]:02X}', base=16)
        
    if lexeme_name == 'LEA':
        operand0 = []
        operand1 = []
        
        # find operands separated by comma
        for i in range(1, len(lexeme)):
            if lexeme[i][1] == ',':
                operand0 = lexeme[1:i]
                operand1 = lexeme[i+1:]
                break
            
        if (len(operand0) >= 3
            and operand0[0][1] in basics.segmentRegistersAddresses):
            generate_segment_register_encoding(operand0[0])
            operand0 = operand0[2:]
            
        if (len(operand0) >= 3
            and operand0[2][1] in basics.segmentRegistersAddresses):
            generate_segment_register_encoding(operand0[2])
            operand0 = operand0[:2] + operand0[3:]
        
        if is_register32(operand0) and is_member(operand1):
            modrm_sib = generate_modrm_sib_encoding(operand1, 0, basics.addressesRegisters32[operand0[0][1]])
            return int(f'8D{modrm_sib["byte"]:02X}', base=16)
        
    if lexeme_name == 'AND':
        operand0 = []
        operand1 = []
        
        # find operands separated by comma
        for i in range(1, len(lexeme)):
            if lexeme[i][1] == ',':
                operand0 = lexeme[1:i]
                operand1 = lexeme[i+1:]
                break
        
        if (len(operand0) >= 3
            and operand0[0][1] in basics.segmentRegistersAddresses):
            generate_segment_register_encoding(operand0[0])
            operand0 = operand0[2:]
            
        if (len(operand0) >= 3
            and operand0[2][1] in basics.segmentRegistersAddresses):
            generate_segment_register_encoding(operand0[2])
            operand0 = operand0[:2] + operand0[3:]
            
        if is_member(operand0) and is_register_eight(operand1):
            modrm_sib = generate_modrm_sib_encoding(operand0, 0, basics.addressesRegisters8[operand1[0][1]])
            return int(f'20{modrm_sib["byte"]:04X}', base=16)
        
        if is_member(operand0) and is_register32(operand1):
            modrm_sib = generate_modrm_sib_encoding(operand0, 0, basics.addressesRegisters32[operand1[0][1]])
            return int(f'21{modrm_sib["byte"]:04X}', base=16)
           
    if lexeme_name == 'MOV':
        operand0 = []
        operand1 = []
        
        # find operands separated by comma
        for i in range(1, len(lexeme)):
            if lexeme[i][1] == ',':
                operand0 = lexeme[1:i]
                operand1 = lexeme[i+1:]
                break
        
        if is_register_eight(operand0) and is_immediate_eight_bit(operand1):
            code_int = int('B0', base=16) + int(basics.addressesRegisters8[operand0[0][1]], base=2)
            code_str = f'{code_int:X}'
            return int(f'{code_str}{handleImmediateConversion(operand1):02X}', base=16)
        
        if is_register32(operand0) and is_immediate_eight_bit(operand1):
            code_int = int('B8', base=16) + int(basics.addressesRegisters32[operand0[0][1]], base=2)
            code_str = f'{code_int:X}'
            return int(f'{code_str}{handleImmediateConversion(operand1):08X}', base=16)
        
        if is_register32(operand0) and is_imm32_range(operand1):
            code_int = int('B8', base=16) + int(basics.addressesRegisters32[operand0[0][1]], base=2)
            code_str = f'{code_int:X}'
            return int(f'{code_str}{handleImmediateConversion(operand1):08X}', base=16)

    if lexeme_name == 'ADD':
        operand0 = []
        operand1 = []
        
        # find operands separated by comma
        for i in range(1, len(lexeme)):
            if lexeme[i][1] == ',':
                operand0 = lexeme[1:i]
                operand1 = lexeme[i+1:]
                break
        
        if (len(operand0) >= 3
            and operand0[0][1] in basics.segmentRegistersAddresses):
            generate_segment_register_encoding(operand0[0])
            operand0 = operand0[2:]
            
        if (len(operand0) >= 3
            and operand0[2][1] in basics.segmentRegistersAddresses):
            generate_segment_register_encoding(operand0[2])
            operand0 = operand0[:2] + operand0[3:]
            
        if is_member(operand0) and is_immediate_eight_bit(operand1):
            modrm_sib = generate_modrm_sib_encoding(operand0, 0, '000')
            operands[1] = f'{handleImmediateConversion(operand1):02X}'
            return int(f'80{modrm_sib["byte"]:02X}', base=16)
        
        if is_member(operand0) and is_imm32_range(operand1):
            modrm_sib = generate_modrm_sib_encoding(operand0, 0, '000')
            operands[1] = f'{handleImmediateConversion(operand1):08X}'
            return int(f'81{modrm_sib["byte"]:02X}', base=16)
        
    if lexeme_name == 'JNZ':
        operand0 = lexeme[1:]
        if vars_offsets[operand0[0][1]] == None:
            return int(f'90'*6, base=16)
        else:
            # return current offset  - offset of label
            jmp_offset = current_offset - vars_offsets[operand0[0][1]]['offset'] + 2 # 2 - size of current instruction
            org = f'{jmp_offset:08b}'
            inverted = ''.join(['0' if x == '1' else '1' for x in org])
            inverted = int(inverted, base=2) + 1
            return int(f'75{(inverted):02X}', base=16)

    return 0

def calculate_mnemonic_encoding(lexeme_list: list):
    result = 0

    # Iterate over each element in lexeme_list
    for i in range(len(lexeme_list)):
        # Check if the fourth element of the sublist is 'Ідентифікатор директиви'
        if lexeme_list[i][3] == 'Ідентифікатор директиви':
            result = processDirective(lexeme_list)
        # Check if the fourth element of the sublist is 'Ідентифікатор мнемокоду машиної інструкції'
        elif lexeme_list[i][3] == 'Ідентифікатор мнемокоду машиної інструкції':
            result = generateOpcode(lexeme_list)

    return result

def populateIdentifiersTable():
    global vars_offsets
    global user_identifiers
    global segments_info
    
    # Mapping of types based on the value in the user identifiers
    type_mapping = {1: "Byte", 2: "Word", 4: "Dword", -1: "Near"}

    # Initialize an empty list for table rows
    table_rows = []
    # Iterate over each item in user_identifiers
    for key, value in user_identifiers.items():
        # Check if key is not in segments_info
        if key not in segments_info:
            data_type = type_mapping[value]
            base_address = vars_offsets[key]['seg']
            offset_hex = f'{vars_offsets[key]["offset"]:04X}'
            table_rows.append([key, data_type, f"{base_address}:{offset_hex}"])
    
    return sorted(table_rows)

def create_logical_segments_table():
    # Initialize an empty list for table rows
    table_rows = []
    # Iterate over each item in segments_info
    for key, value in segments_info.items():
        table_rows.append([key, 32, f'{value:04X}'])
        
    return sorted(table_rows)

def printFirstView(lexemes_tables: list, sentence_structures_table: list, row_list: list):
    processIdentifiersAndDirectives(lexemes_tables, sentence_structures_table)
    global current_offset
    global to_print
    global vars_offsets
    global operands
    global operand_ovveride
    global segment_ovveride
    global address_ovveride
    global current_segment
    
    # Open file for write 'result\first_view.txt'
    with open('result\\first_view.txt', 'w') as file:
        print('First view:', file=file)
        print(file=file)
        
        # Iterate over each element in lexemes_tables
        for i in range(len(lexemes_tables)):
            lex = lexemes_tables[i]

            # Calculate mnemonic in hex
            hex_menmonic_int = calculate_mnemonic_encoding(lex)
            hex_mnemonic_str = f'{hex_menmonic_int:X}' if hex_menmonic_int != 0 else ''
            
            hex_mnemonic_str = hex_mnemonic_str if len(hex_mnemonic_str) % 2 == 0 else '0' + hex_mnemonic_str

            print(f'{i + 1:03}  ', file=file, end='')

            # Print current offset in 8 zeros
            print(f'{current_offset:08X}  ', file=file, end='')
            
            if operand_ovveride != '':
                to_print += operand_ovveride
                operand_ovveride = ''
                
            if segment_ovveride != '':
                to_print += segment_ovveride
                segment_ovveride = ''
                
            if address_ovveride != '':
                to_print += address_ovveride
                address_ovveride = ''

            current_offset += len(to_print) // 2
            
            to_print += hex_mnemonic_str
            for i_b in range(len(operands)):
                if operands[i_b] != None:
                    to_print += f' {operands[i_b]}'

                    if operands[i_b][-1] == 'r':
                        current_offset += (len(operands[i_b]) - 1) // 2
                    else:
                        current_offset += len(operands[i_b]) // 2

                    operands[i_b] = None

            # Check if the first element of lex is 'Ідентифікатор користувача або не визначений' and the second element is ':'
            if lex[0][3] == 'Ідентифікатор користувача або не визначений' and lex[1][1] == ':':
                vars_offsets[lex[0][1]] = {'seg': current_segment, 'offset': current_offset}

            print(f'{to_print:30}  ', file=file, end='')
            to_print = ''

            # Print lexeme
            print(f'{row_list[i]}', file=file, end='')

            current_offset += len(hex_mnemonic_str) // 2

            print(file=file)
        print(file=file)
        header = ['Symbol Name', 'Type', 'Value']
        display_2d_data([header] + populateIdentifiersTable(), file=file)
        
        print(file=file)
        header = ['Segment', 'Size', 'Align']
        display_2d_data([header] + create_logical_segments_table(), file=file)
        
        print(file=file)
        print(f'Errors: {error_num}', file=file)
    return vars_offsets
