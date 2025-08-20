import ast

class A(ast.NodeTransformer):

	def d(__ngocuyencoder__, __uyencoder__):
		__ngocuyencoder__.generic_visit(__uyencoder__)
		if hasattr(__uyencoder__, 'body') and isinstance(__uyencoder__.body, list):
			__uyencoder__.body = [s for s in __uyencoder__.body if s is not None]
		return __uyencoder__

	def vs(__ngocuyencoder__, __uyencoder__):
		__uyencoder__ = __ngocuyencoder__.d(__uyencoder__)
		if __uyencoder__.body and isinstance(__uyencoder__.body[0], ast.Expr) and isinstance(__uyencoder__.body[0].value, ast.Constant) and isinstance(__uyencoder__.body[0].value.value, str):
			__uyencoder__.body.pop(0)
		return __uyencoder__

	def func(__ngocuyencoder__, __uyencoder__):
		__uyencoder__ = __ngocuyencoder__.d(__uyencoder__)
		if __uyencoder__.body and isinstance(__uyencoder__.body[0], ast.Expr) and isinstance(__uyencoder__.body[0].value, ast.Constant) and isinstance(__uyencoder__.body[0].value.value, str):
			__uyencoder__.body.pop(0)
		return __uyencoder__

	def balamon(__ngocuyencoder__, __uyencoder__):
		return __ngocuyencoder__.func(__uyencoder__)

	def idk(__ngocuyencoder__, __uyencoder__):
		__uyencoder__ = __ngocuyencoder__.d(__uyencoder__)
		if __uyencoder__.body and isinstance(__uyencoder__.body[0], ast.Expr) and isinstance(__uyencoder__.body[0].value, ast.Constant) and isinstance(__uyencoder__.body[0].value.value, str):
			__uyencoder__.body.pop(0)
		return __uyencoder__

	def visit_Expr(__ngocuyencoder__, __uyencoder__):
		if isinstance(__uyencoder__.value, ast.Constant) and isinstance(__uyencoder__.value.value, str):
			return None
		return __uyencoder__

def b(c):
	f = ast.parse(c)
	f = A().visit(f)
	ast.fix_missing_locations(f)
	g = ast.unparse(f)
	return g
try:
	file = __import__('sys').argv[1]
	tfile = open(file, 'r', encoding='utf8').read()
	t__file__ = file.split('\\')[-1]
except:
	__file__ = __file__.split('\\')[-1]
	print(f'using : python {__file__} <filename> ')
	quit()
try:
	x = b(tfile)
except:
	print('CANNOT FORMAT A CODE')
tf = f'fm_{t__file__}'
with open(f'{tf}', 'w', encoding='utf-8') as i:
	i.write(str(x))
	print(f'a file write in {tf}')
