#chapter 7 and 8 of nand2tetris

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

BASE_ADDRESS_LOCATIONS = {"stack":0, "local": 1, "argument": 2, "pointer":3, "temp": 5, "static": 16}

INITIAL_POINTERS = {"stack": 256, "local": 300, "argument": 400}

OPERATIONS = {"add": "+", "sub": "-", "or": "|", "and": "&"}

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



def read_vm_code_line(code_line, line_number = None):
	code_split = [x for x in str(code_line).split() if x != ""]

	print "code_split", code_split

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
	except Exception as e:
		print str(e)

	error_log = "failed to parse line " + code_line

	raise Exception(error_log)

	#seems useless
	return ""

if __name__ == '__main__':
	#test for now TODO: add argparse which reads given file
	print read_vm_code_line("add")

