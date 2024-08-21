from db_setup import db

class Produto(db.Model):
    __tablename__ = 'produto'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo_barras = db.Column(db.String(20), unique=True, nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    
    def __repr__(self):
        return f'<Produto {self.nome}>'

class Setor(db.Model):
    __tablename__ = 'setor'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    
    def __repr__(self):
        return f'<Setor {self.nome}>'
