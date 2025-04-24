asmTestFile = 'soft\\test1.asm'

resultFile = 'result\\result.txt'

identifierCharacterSet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890'

identifierLengthLimit = 5

assemblyOpCodes = [
    'SCASB',
    'DEC',
    'INC',
    'LEA',
    'AND',
    'MOV',
    'ADD',
    'JNZ'
]

registerInfo = {
    'AX':  'Регістр 16',
    'BX':  'Регістр 16',
    'CX':  'Регістр 16',
    'DX':  'Регістр 16',
    'SP':  'Регістр 16',
    'BP':  'Регістр 16',
    'SI':  'Регістр 16',
    'DI':  'Регістр 16',
    'AL':  'Регістр 8',
    'BL':  'Регістр 8',
    'CL':  'Регістр 8',
    'DL':  'Регістр 8',
    'AH':  'Регістр 8',
    'BH':  'Регістр 8',
    'CH':  'Регістр 8',
    'DH':  'Регістр 8'
}


segmentRegistersDescription = {
    'ES': 'Регістр сегменту',
    'CS': 'Регістр сегменту',
    'SS': 'Регістр сегменту',
    'DS': 'Регістр сегменту',
    'FS': 'Регістр сегменту',
}

asmCodeDirectives = [
    'END', 
    'SEGMENT',
    'ENDS',
    'EQU',
    'DB', 
    'DW', 
    'DD'
]

punctuationCharacters = [
    ':', 
    ',', 
    '(', 
    ')', 
    '[', 
    ']', 
    '+', 
    '-', 
    '*', 
    ':'
]

addressesRegisters32 = {
    'EAX': '000',
    'ECX': '001',
    'EDX': '010',
    'EBX': '011',
    'ESP': '100',
    'EBP': '101',
    'ESI': '110',
    'EDI': '111'
}

addressesRegisters8 = {
    'AL': '000',
    'CL': '001',
    'DL': '010',
    'BL': '011',
    'AH': '100',
    'CH': '101',
    'DH': '110',
    'BH': '111'
}

segmentRegistersAddresses = {
    'ES': '000',
    'CS': '001',
    'SS': '010',
    'DS': '011',
    'FS': '100',
    'GS': '101'
}

