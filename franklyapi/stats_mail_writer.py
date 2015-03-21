def make_html_table(results):
	resp = """
	<table style = '	font-size:14px;
			margin: 0px auto;
			width: 97%;
			max-width: 100%;
			margin-bottom: 20px;
			border-spacing: 0;
			border-collapse: collapse;'>
			"""
	resp += """<tr style='border-bottom:#eee 1px solid;'>"""
	for key in results.keys():
		resp += """<th style='text-align:left;'>{}</th>""".format(key)
	resp += '</tr>'
	for row in results:
		resp += """<tr style='border-bottom:#eee 1px solid;'>"""
		for data in row:
			resp += '<td>{}</td>'.format(data)
		resp += '</tr>'
	resp += '</table>'
	return resp
def add_style():
	return """
		<style>
		body {
			
		}
		table{
		}
		table>thead>tr>th, table>tbody>tr>th, table>tfoot>tr>th, table>thead>tr>td, table>tbody>tr>td, table>tfoot>tr>td {
			padding: 8px;
			line-height: 1.42857143;
			vertical-align: top;
			border-top: 1px solid #ddd;
		}
		th {
			text-align: left;
		}
		td, th {
			padding: 0;
		}
		



	</style>"""
def make_panel(title='',content=''):
	heading = """
		<div class = 'panel-heading' style='color: #31708f;
			background-color: #d9edf7;
			border-color: #bce8f1;
			padding: 10px 15px;
			border-bottom: 1px solid transparent;
			border-top-left-radius: 3px;
			border-top-right-radius: 3px;'>

			<h3 class = 'panel-title' style='
				margin-top: 0;
				margin-bottom: 0;
				font-size: 16px;
				color: inherit;'>
				{}
			</h3> 

		</div>
		""".format(title)

	if title=='':
		heading=''

	resp = """

	<div class='panel' style='
			width:70%;
			margin:10px auto;
			margin-bottom: 20px;
			background-color: #fff;
			border: 1px solid transparent;
			border-radius: 4px;
			-webkit-box-shadow: 0 1px 1px rgba(0,0,0,.05);
			box-shadow: 0 1px 1px rgba(0,0,0,.05);
			border-color: #bce8f1;'>
		{}
		{}
	</div>

	""".format(heading, content)
	
	return resp
