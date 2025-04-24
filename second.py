import basics

def modify_second_view(variable_offsets: dict):
    # Open the first view file for reading and the second view file for writing
    with open('result\\first_view.txt', 'r') as first_view_file, open('result\\second_view.txt', 'w') as second_view_file:
        # If '9090909090' is found in the file, it will be replaced with the offset of the label

        # Iterate over each line in first_view.txt
        for line_content in first_view_file:
            # Check if '9090909090' (JMP) is present in the line
            if '909090909090' in line_content:
                # Split the line into words
                words_in_line = line_content.split()
                # Find the offset of the label
                label_offset = variable_offsets[words_in_line[4].upper()]["offset"]
                # Calculate the offset as an integer
                temp_offset = int(words_in_line[1], base=16)
                calculated_offset = label_offset - temp_offset - 6 + 4
                # Create a new line with the calculated offset
                new_line_content = f'75{calculated_offset:02X}90909090'
                # Replace '90'*6 in the original line with the new line content
                line_content = line_content.replace('90'*6, new_line_content)
                
            # Write the modified line to second_view.txt
            second_view_file.write(line_content)
