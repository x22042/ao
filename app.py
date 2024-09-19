import os
from flask import Flask, request, render_template, redirect, url_for
import subprocess
from pdf2text import convert_pdf_to_text  # pdf2text.py の関数をインポート
from T2Q import generate_and_extract_cloze_test

app = Flask(__name__,static_folder='static')

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
TEXT_FOLDER = os.path.join(os.path.dirname(__file__), 'texts')  # テキストファイルの保存先
QTEXT_FOLDER = os.path.join(os.path.dirname(__file__), 'Qtexts')  # 穴埋め問題ファイルの保存先
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['TEXT_FOLDER'] = TEXT_FOLDER
app.config['QTEXT_FOLDER'] = QTEXT_FOLDER
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def upload_form():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'pdfFile' not in request.files or 'filename' not in request.form:
        return 'ファイル名またはPDFが選択されていません'
    
    file = request.files['pdfFile']
    custom_filename = request.form['filename'].strip()  # ユーザーが入力したファイル名
    if file.filename == '':
        return 'PDFファイルが選択されていません'

    if custom_filename == '':
        return 'ファイル名を入力してください'
    
    if file and allowed_file(file.filename):
        filename = file.filename
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)
        # print("\nFILENAME" + filename + "\n")
        # print("\nCUSTOM_FILENAME" + custom_filename + "\n")
        # print("\nSAVEPATH" + save_path + "\n")


        txt_filepath = convert_pdf_to_text(save_path, app.config['TEXT_FOLDER'], custom_filename)
        # print("TXTPATH" + txt_filepath + "\n")

        generate_filename = os.path.basename(txt_filepath)
        # print("GENERATE_FILENAME" + generate_filename + "\n")

        generate_and_extract_cloze_test(txt_filepath, generate_filename)

        # 生成されたテキストファイルを読み込み、新しいページに表示
        return redirect(url_for('show_text', filename=os.path.basename(txt_filepath)))
        # return {"redirectUrl": url_for('show_text', filename=generate_filename)}
    else:
        return '許可されていないファイル形式です'

# テキストファイル一覧
@app.route('/texts')
def list_text_files():
    files = os.listdir(app.config['TEXT_FOLDER'])
    text_files = [f for f in files if f.endswith('.txt')]
    return render_template('list_files.html', files=text_files)

    

# テキストファイルの内容
@app.route('/text/<filename>')
def show_text(filename):

    qtxt_filepath = os.path.join(app.config['QTEXT_FOLDER'], filename)
    print("QTXTPATH" + qtxt_filepath + "\n")

    if os.path.exists(qtxt_filepath):
        with open(qtxt_filepath, 'r', encoding='utf-8') as file:
            text_content = file.read()
        return render_template('show_text.html', content=text_content)
    else:
        return 'ファイルが見つかりませんでした'

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    if not os.path.exists(app.config['TEXT_FOLDER']):
        os.makedirs(app.config['TEXT_FOLDER'])
    app.run(debug=True)
