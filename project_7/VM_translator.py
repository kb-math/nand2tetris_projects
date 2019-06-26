#chapter 7 and 8 of nand2tetris

import argparse

with open("asm_templates/set_value.template") as f:
	set_value_template = f.read()

with open("asm_templates/push_constant.template") as f:
	push_constant_template = f.read()

with open("asm_templates/push_segment_i.template") as f:
	push_segment_i_template = f.read()

with open("asm_templates/pop_segment_i.template") as f:
	pop_segment_i_template = f.read()

with open("asm_templates/arithmetic.template") as f:
	arithmetic_template = f.read()

with open("asm_templates/unary.template") as f:
	operator_template = f.read()

with open("asm_templates/comparison.template") as f:
	comparison_template = f.read()

BASE_ADDRESS_LOCATIONS = {"stack":0, "local": 1, "argument": 2, "pointer":3, "temp": 5, "static": 16}

INITIAL_POINTERS = {"stack": 256, "local": 300, "argument": 400}

OPERATIONS = {"add": "+", "sub": "-", "or": "|", "and": "&"}

OPERATORS = {"not": "!", "neg": "-"}

# i.e., < is lt, = is eq, > is gt
COMPARISONS = {"lt": "JLT", "eq": "JEQ", "gt": "JGT"}

LABEL_COUNTER = 0

#put <value> into RAM[<address>]
def set_value_code(address, value):
	code_str = str(set_value_template)
	code_str = code_str.replace("<address>", str(address))
	code_str = code_str.replace("<value>", str(value))

	return code_str

def push_constant_code(i):
	code_str = str(push_constant_template)
	code_str = code_str.replace("<i>", str(i))

	return code_str

def push_segment_i_code(segment, i):
	code_str = str(push_segment_i_template)
	segment_base_address_location = BASE_ADDRESS_LOCATIONS[segment]
	code_str = code_str.replace("<segment>", str(segment))
	code_str = code_str.replace("<segment_base_address_location>", str(segment_base_address_location))
	code_str = code_str.replace("<i>", str(i))

	return code_str

def pop_segment_i_code(segment, i):
	code_str = str(pop_segment_i_template)
	segment_base_address_location = BASE_ADDRESS_LOCATIONS[segment]
	code_str = code_str.replace("<segment>", str(segment))
	code_str = code_str.replace("<segment_base_address_location>", str(segment_base_address_location))
	code_str = code_str.replace("<i>", str(i))

	return code_str

def arithmetic_code(operation):
	code_str = str(arithmetic_template)
	code_str = code_str.replace("<operation>", str(operation))
	operation_symbol = OPERATIONS[operation]
	code_str = code_str.replace("<operation_symbol>", str(operation_symbol))

	return code_str

def operator_code(operator):
	code_str = str(operator_template)
	code_str = code_str.replace("<operator>", str(operator))
	operator_symbol = OPERATORS[operator]
	code_str = code_str.replace("<operator_symbol>", str(operator_symbol))

	return code_str

def comparison_code(comparison):
	global LABEL_COUNTER

	code_str = str(comparison_template)
	code_str = code_str.replace("<comparison>", str(comparison))
	comparison_jump_symbol = COMPARISONS[comparison]
	code_str = code_str.replace("<comparison_jump_symbol>", str(comparison_jump_symbol))

	# replace <label> with string label_<LABEL_COUNTER>_label and increment to avoid
	#clashes between labels
	label = "jump_here_if_comparison_is_true"
	label_indexed = "label_" + str(LABEL_COUNTER) + "_" + label
	code_str = code_str.replace(label, label_indexed)
	LABEL_COUNTER += 1

	label = "end_comparison_block"
	label_indexed = "label_" + str(LABEL_COUNTER) + "_" + label
	code_str = code_str.replace(label, label_indexed)
	LABEL_COUNTER += 1

	return code_str


def read_vm_code_line(code_line):
	code_split = [x for x in str(code_line).split() if x != ""]

	try:
		#empy line
		if not code_split:
			return ""

		if code_split[0][0] == "/":
			if code_split[0][1] == "/":
				#it is a comment, should we keep or remove it?
				return code_line

		first_keyword = code_split[0]

		if first_keyword == "push":
			second_keyword = code_split[1]
			if second_keyword == "constant":
				return push_constant_code(code_split[2])
			else:
				#second keyword must be a segment
				return push_segment_i_code(second_keyword, code_split[2])

		if first_keyword == "pop":
			second_keyword = code_split[1]
			if second_keyword in BASE_ADDRESS_LOCATIONS.keys():
				return pop_segment_i_code(second_keyword, code_split[2])
		if first_keyword in OPERATIONS.keys():
			return arithmetic_code(first_keyword)
		if first_keyword in OPERATORS.keys():
			return operator_code(first_keyword)
		if first_keyword in COMPARISONS.keys():
			return comparison_code(first_keyword)
	except Exception as e:
		print str(e)

	error_log = "failed to parse line " + code_line

	raise Exception(error_log)

if __name__ == '__main__':
	
	parser = argparse.ArgumentParser()
	parser.add_argument('vm_code_file', help = ".vm file path to be translated to .asm")

	args = parser.parse_args()

	source_code_fname = args.vm_code_file
	with open(source_code_fname) as f:
		source_code = f.read()
		source_code_lines = source_code.split("\n")

	line_number = 1
	with open(source_code_fname + ".asm", 'wa') as output_asm_file:
		for code_line in source_code_lines:
			try:
				asm_code_line = read_vm_code_line(code_line)
			except Exception as e:
				print "failed at line", line_number
				output_asm_file.write("COMPILATION_FAILED!")
				raise Exception(str(e))
		
			output_asm_file.write(asm_code_line + "\n")
			line_number += 1

	print "finished compiling ", source_code_fname

