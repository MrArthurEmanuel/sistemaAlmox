from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, send_file
import pdfkit
from io import BytesIO
from db_setup import db
from models import Produto, Setor
from sqlalchemy.orm import Session
import json
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:teste123@localhost/almoxarifado'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui'

pdfkit_config = pdfkit.configuration(wkhtmltopdf='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')
db.init_app(app)

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro_produto():
    if request.method == 'POST':
        codigo_barras = request.form['codigo_barras']
        nome = request.form['nome']
        quantidade = request.form['quantidade']
        
        produto = Produto(
            codigo_barras=codigo_barras,
            nome=nome,
            quantidade=quantidade
        )
        db.session.add(produto)
        db.session.commit()
        flash('Produto cadastrado com sucesso!', 'success')
        return redirect(url_for('listar_produtos'))
    return render_template('cadastro.html')

@app.route('/produtos')
def listar_produtos():
    produtos = Produto.query.all()
    return render_template('produtos.html', produtos=produtos)

@app.route('/')
def exibir_index():
    return render_template('index.html')

@app.route('/saida', methods=['GET', 'POST'])
def saida_produto():
    setores = Setor.query.all()
    success_message = "Saída com sucesso"
    error_message = "Alguns produtos solicitados não estão com estoque suficiente"
    produtos_para_corrigir = []
    produtos_para_pdf = []  # Lista para armazenar os produtos para o PDF

    if request.method == 'POST':
        setor_id = request.form.get('setor_id')
        produto_ids = request.form.getlist('produto_id[]')
        quantidades_saida = request.form.getlist('quantidade_saida[]')

        erros_encontrados = False
        setor = Setor.query.get(setor_id)
        data_hora = datetime.now().strftime('%d/%m/%Y %H:%M:%S')


        for produto_id, quantidade_saida in zip(produto_ids, quantidades_saida):
            produto = Produto.query.get(produto_id)
            quantidade_saida = int(quantidade_saida)

            if produto and produto.quantidade >= quantidade_saida:
                produto.quantidade -= quantidade_saida
                produtos_para_pdf.append({
                    'codigo_barras': produto.codigo_barras,
                    'nome': produto.nome,
                    'quantidade_solicitada': quantidade_saida
                })
            else:
                produtos_para_corrigir.append({
                    'id': produto.id if produto else None,
                    'nome': produto.nome if produto else 'Desconhecido',
                    'quantidade': quantidade_saida,
                    'quantidade_atual': produto.quantidade if produto else 0
                })
                erros_encontrados = True

        if not erros_encontrados:
            db.session.commit()
            # Gerar o PDF automaticamente após o commit
            rendered = render_template('saida_pdf.html', 
                                       produtos=produtos_para_pdf,
                                       setor=setor.nome if setor else 'Não especificado',
                                       data_pedido=data_hora)
            options = {
                'page-size': 'A4',
                'margin-top': '0mm',
                'margin-right': '0mm',
                'margin-bottom': '0mm',
                'margin-left': '0mm'
            }
            pdf = pdfkit.from_string(rendered, False, configuration=pdfkit_config, options=options)

            if not pdf:
                return "Erro na geração do PDF", 500

            return send_file(BytesIO(pdf), download_name='Requisição - Setor: .pdf', as_attachment=True)
        
        return render_template(
            'saida.html',
            produtos=Produto.query.all(),
            setores=setores,
            success=success_message,
            error=error_message,
            produtos_para_corrigir=produtos_para_corrigir
        )

    return render_template(
        'saida.html',
        produtos=Produto.query.all(),
        setores=setores,
        produtos_para_corrigir=[]
    )


@app.route('/quantidade_produto/<int:produto_id>', methods=['GET'])
def quantidade_produto(produto_id):
    produto = Produto.query.get(produto_id)
    
    if produto:
        return jsonify({'quantidade': produto.quantidade})
    return jsonify({'quantidade': 0})

@app.route('/atualizar', methods=['GET', 'POST'])
def selecionar_produto_atualizar():
    if request.method == 'POST':
        produto_id = request.form['produto_id']
        return redirect(url_for('atualizar_produto', produto_id=produto_id))
    
    produtos = Produto.query.all()
    return render_template('selecionar_produto.html', produtos=produtos)

@app.route('/atualizar/<int:produto_id>', methods=['GET', 'POST'])
def atualizar_produto(produto_id):
    produto = Produto.query.get_or_404(produto_id)

    if request.method == 'POST':
        produto.codigo_barras = request.form['codigo_barras']
        produto.nome = request.form['nome']
        produto.quantidade = request.form['quantidade']
        db.session.commit()
        flash('Produto atualizado com sucesso!', 'success')
        return redirect(url_for('listar_produtos'))

    return render_template('atualizar.html', produto=produto)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    # Configura o SSL usando os arquivos gerados
    app.run(host='0.0.0.0', port=5000, debug=True)

