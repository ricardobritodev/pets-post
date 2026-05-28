"""
models/user.py — Model de Usuário

Representa a tabela 'users' no banco de dados.
Cada linha da tabela é uma instância da classe User.

O UserMixin do Flask-Login adiciona os métodos necessários para autenticação:
  - is_authenticated: True se o usuário está logado
  - is_active: True se a conta está ativa
  - is_anonymous: True se é um visitante sem conta
  - get_id(): retorna o ID do usuário como string
"""

from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db, login_manager


class User(UserMixin, db.Model):
    """Model de usuário — armazena dados de cadastro e autenticação."""

    # Nome da tabela no banco de dados
    __tablename__ = 'users'

    # -----------------------------------------------
    # Colunas da tabela
    # -----------------------------------------------

    # Chave primária — identificador único de cada usuário
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Nome completo do usuário
    name = db.Column(db.String(100), nullable=False)

    # Email — usado para login, deve ser único
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)

    # Senha armazenada como hash (nunca guardamos a senha em texto puro!)
    password_hash = db.Column(db.String(256))

    # Perfil: 'admin' tem acesso ao painel administrativo, 'user' é usuário comum
    role = db.Column(
        db.Enum('admin', 'user', name='user_role'),
        default='user',
        nullable=False
    )

    # Telefone para contato (opcional)
    phone = db.Column(db.String(20), nullable=True)

    # URL da foto de perfil (opcional)
    avatar_url = db.Column(db.String(256), nullable=True)

    # Se False, o usuário foi desativado pelo admin e não consegue logar
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Data e hora do cadastro — preenchida automaticamente
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # -----------------------------------------------
    # Relacionamentos
    # -----------------------------------------------

    # Um usuário pode ter vários posts de pets (one-to-many)
    # 'back_populates' cria o acesso reverso: post.user retorna o User
    posts = db.relationship('PetPost', back_populates='user', lazy='dynamic')
    adoption_posts = db.relationship('AdoptionPost', back_populates='user', lazy='dynamic')

    # -----------------------------------------------
    # Métodos
    # -----------------------------------------------

    def set_password(self, password):
        """
        Gera o hash da senha e salva.
        NUNCA armazene senhas em texto puro no banco de dados!
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        Verifica se a senha informada corresponde ao hash armazenado.
        Retorna True se a senha está correta, False caso contrário.
        """
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        """Retorna True se o usuário tem perfil de administrador."""
        return self.role == 'admin'

    def __repr__(self):
        """Representação útil para debug no terminal."""
        return f'<User {self.email}>'

    # TODO: Adicionar campo de verificação de email (email_verified)
    # TODO: Adicionar integração com OAuth (Google, Facebook) para login social
    # TODO: Adicionar campo de bio/descrição para perfil público


# -----------------------------------------------
# Função necessária para o Flask-Login
# -----------------------------------------------

@login_manager.user_loader
def load_user(user_id):
    """
    Diz ao Flask-Login como carregar um usuário pelo ID.
    É chamado automaticamente a cada requisição para verificar a sessão.
    """
    return db.session.get(User, int(user_id))
