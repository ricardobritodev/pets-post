"""
run.py — Ponto de entrada da aplicação PetPost

Execute este arquivo para iniciar o servidor de desenvolvimento:
    python run.py

Ou use o Flask CLI:
    flask run
"""

from app import create_app
from app.extensions import db

# Cria a instância da aplicação usando o padrão Application Factory
app = create_app()


@app.cli.command('create-db')
def create_db():
    """
    Cria todas as tabelas no banco de dados diretamente.

    Use este comando quando flask db upgrade não funcionar:
        flask create-db
    """
    with app.app_context():
        db.create_all()
        print('✅ Tabelas criadas com sucesso!')
        print('   Agora rode: python seeds.py')


if __name__ == '__main__':
    # debug=True recarrega o servidor automaticamente ao salvar arquivos
    # NÃO use debug=True em produção!
    app.run(debug=True)
