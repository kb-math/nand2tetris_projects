#chapter 7 and 8 of nand2tetris

import argparse
import os

with open("asm_templates/set_value.template") as f:
	set_value_template = f.read()

with open("asm_templates/push_constant.template") as f:
	push_constant_template = f.read()

with open("asm_templates/push_segment_i.template") as f:
	push_segment_i_template = f.read()

with open("asm_templates/pop_segment_i.template") as f:
	pop_segment_i_template = f.read()

with open("asm_templates/push_fixed_segment_i.template") as f:
	push_fixed_segment_i_template = f.read()

with open("asm_templates/pop_fixed_segment_i.template") as f:
	pop_fixed_segment_i_template = f.read()

with open("asm_templates/push_static.template") as f:
	push_static_template = f.read()

with open("asm_templates/pop_static.template") as f:
	pop_static_template = f.read()

with open("asm_templates/arithmetic.template") as f:
	arithmetic_template = f.read()

with open("asm_templates/unary.template") as f:
	operator_template = f.read()

with open("asm_templates/comparison.template") as f:
	comparison_template = f.read()

BASE_ADDRESS_LOCATIONS = {"stack":0, "local": 1, "argument": 2, "this":3, "that": 4}

FIXED_BASES = {"pointer": 3, "temp": 5, "static": 16}

OPERATIONS = {"add": "+", "sub": "-", "or": "|", "and": "&"}

OPERATORS = {"not": "!", "neg": "-"}

# i.e., < is lt, = is eq, > is gt
COMPARISONS = {"lt": "JLT", "eq": "JEQ", "gt": "JGT"}

class AssemblyCodeGenerator(object):
	def __init__(self, output_asm_file_path):
		self._LABEL_COUNTER = 0
		self._output_asm_file = open(output_asm_file_path, 'wa')
		self._current_vm_fname = ""

	def close_output_file(self):
		self._output_asm_file.close()

	def open_vm_file(self, file_path):
		with open(file_path) as f:
			source_code = f.read()
		
		#clear from previous file
		self._source_code_lines = []
		self._source_code_lines = source_code.split("\n")

		self._current_vm_fname = os.path.basename(file_path)

	def translate_file(self, file_path):
		line_number = 1
		self.open_vm_file(file_path)
		for code_line in self._source_code_lines:
			try:
				asm_code_line = self.read_vm_code_line(code_line)
			except Exception as e:
				print "failed at line", line_number, "in file", file_path
				self._output_asm_file.write("COMPILATION_FAILED!")
				raise Exception(str(e))
		
			self._output_asm_file.write(asm_code_line + "\n")
			line_number += 1


	def create_static_name(self, i):
		return self._current_vm_fname + ".static." + str(i)

	def create_label(self, original_label):
		#To prevent name clashes from different instances of same template
		# we pre-append with label_LABEL_COUNTER- and increment LABEL_COUNTER
		new_label = "label_" + str(self._LABEL_COUNTER) + "-" + original_label
		self._LABEL_COUNTER += 1
		return new_label


	#put <value> into RAM[<address>]
	def set_value_code(self, address, value):
		code_str = str(set_value_template)
		code_str = code_str.replace("<address>", str(address))
		code_str = code_str.replace("<value>", str(value))

		return code_str

	def push_constant_code(self, i):
		code_str = str(push_constant_template)
		code_str = code_str.replace("<i>", str(i))

		return code_str

	def push_segment_i_code(self, segment, i):
		#quite annoying that temp and static don't have a pointer like LCL, ARG etc.
		#requires a different code
		if segment == "static":
			static_var_name = self.create_static_name(i)
			code_str = str(push_static_template)
			code_str = code_str.replace("<static>", static_var_name)

		elif segment in FIXED_BASES.keys():
			code_str = str(push_fixed_segment_i_template)
			segment_base = FIXED_BASES[segment]
			code_str = code_str.replace("<fixed_segment>", str(segment))
			code_str = code_str.replace("<fixed_segment_base>", str(segment_base))
			code_str = code_str.replace("<i>", str(i))
		elif segment in BASE_ADDRESS_LOCATIONS.keys():
			code_str = str(push_segment_i_template)
			segment_base_address_location = BASE_ADDRESS_LOCATIONS[segment]
			code_str = code_str.replace("<segment>", str(segment))
			code_str = code_str.replace("<segment_base_address_location>", str(segment_base_address_location))
			code_str = code_str.replace("<i>", str(i))
		else:
			raise Exception ("unknown segment", segment) 

		return code_str

	#TODO: code duplication with pop and push? (apart from template name really)
	def pop_segment_i_code(self, segment, i):
		#quite annoying that temp and static don't have a pointer like LCL, ARG etc.
		#requires a different code
		if segment == "static":
			static_var_name = self.create_static_name(i)
			code_str = str(pop_static_template)
			code_str = code_str.replace("<static>", static_var_name)
		elif segment in FIXED_BASES.keys():
			code_str = str(pop_fixed_segment_i_template)
			segment_base = FIXED_BASES[segment]
			code_str = code_str.replace("<fixed_segment>", str(segment))
			code_str = code_str.replace("<fixed_segment_base>", str(segment_base))
			code_str = code_str.replace("<i>", str(i))
		elif segment in BASE_ADDRESS_LOCATIONS.keys():
			code_str = str(pop_segment_i_template)
			segment_base_address_location = BASE_ADDRESS_LOCATIONS[segment]
			code_str = code_str.replace("<segment>", str(segment))
			code_str = code_str.replace("<segment_base_address_location>", str(segment_base_address_location))
			code_str = code_str.replace("<i>", str(i))
		else:
			raise Exception ("unknown segment", segment)

		return code_str

	def arithmetic_code(self, operation):
		code_str = str(arithmetic_template)
		code_str = code_str.replace("<operation>", str(operation))
		operation_symbol = OPERATIONS[operation]
		code_str = code_str.replace("<operation_symbol>", str(operation_symbol))

		return code_str

	def operator_code(self, operator):
		code_str = str(operator_template)
		code_str = code_str.replace("<operator>", str(operator))
		operator_symbol = OPERATORS[operator]
		code_str = code_str.replace("<operator_symbol>", str(operator_symbol))

		return code_str

	def comparison_code(self, comparison):
		code_str = str(comparison_template)
		code_str = code_str.replace("<comparison>", str(comparison))
		comparison_jump_symbol = COMPARISONS[comparison]
		code_str = code_str.replace("<comparison_jump_symbol>", str(comparison_jump_symbol))

		# replace <label> with string label_<self._LABEL_COUNTER>_label and increment to avoid
		#clashes between labels
		label = "jump_here_if_comparison_is_true"
		label_indexed = self.create_label(label)
		code_str = code_str.replace(label, label_indexed)

		label = "end_comparison_block"
		label_indexed = self.create_label(label)
		code_str = code_str.replace(label, label_indexed)

		return code_str


	def read_vm_code_line(self, code_line):
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
					return self.push_constant_code(code_split[2])
				else:
					#second keyword must be a segment
					return self.push_segment_i_code(second_keyword, code_split[2])

			if first_keyword == "pop":
				second_keyword = code_split[1]
				return self.pop_segment_i_code(second_keyword, code_split[2])
			if first_keyword in OPERATIONS.keys():
				return self.arithmetic_code(first_keyword)
			if first_keyword in OPERATORS.keys():
				return self.operator_code(first_keyword)
			if first_keyword in COMPARISONS.keys():
				return self.comparison_code(first_keyword)
		except Exception as e:
			print str(e)

		error_log = "failed to parse line " + code_line

		raise Exception(error_log)

if __name__ == '__main__':
	
	parser = argparse.ArgumentParser()
	parser.add_argument('vm_code_file', help = ".vm file path to be translated to .asm")

	args = parser.parse_args()
	source_code_fname = args.vm_code_file

	output_file_path = source_code_fname + ".asm"
	code_generator = AssemblyCodeGenerator(output_file_path)

	code_generator.translate_file(source_code_fname)

	code_generator.close_output_file()

	print "finished compiling ", source_code_fname

