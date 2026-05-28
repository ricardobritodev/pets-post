"""
forms/post_forms.py — Formulário de Post de Pet

Valida os dados do anúncio antes de salvar no banco.
"""

from flask_wtf import FlaskForm
from flask_wtf.file import MultipleFileField, FileAllowed
from wtforms import (
    StringField, TextAreaField, SelectField, SubmitField
)
from wtforms.validators import DataRequired, Optional, Length, Email, ValidationError


class PetPostForm(FlaskForm):
    """Formulário para criar ou editar um post de pet perdido/encontrado."""

    title = StringField(
        'Título do anúncio',
        validators=[
            DataRequired(message='O título é obrigatório.'),
            Length(max=150, message='O título deve ter no máximo 150 caracteres.')
        ],
        render_kw={'placeholder': 'Ex: Cachorro perdido no Parque Ibirapuera'}
    )

    description = TextAreaField(
        'Descrição',
        validators=[
            DataRequired(message='A descrição é obrigatória.')
        ],
        render_kw={
            'placeholder': 'Descreva o pet, como ele estava, onde foi visto, características marcantes...',
            'rows': 5
        }
    )

    status = SelectField(
        'Situação',
        choices=[
            ('lost', '🔴 Meu pet está perdido'),
            ('found', '🟢 Encontrei um pet')
        ],
        validators=[DataRequired()]
    )

    pet_name = StringField(
        'Nome do pet (se souber)',
        validators=[Optional(), Length(max=100)],
        render_kw={'placeholder': 'Ex: Rex, Mimi, Bolinha...'}
    )

    pet_type = SelectField(
        'Tipo de animal',
        choices=[
            ('dog', 'Cachorro'),
            ('cat', 'Gato'),
            ('bird', 'Pássaro'),
            ('other', 'Outro')
        ],
        validators=[DataRequired(message='Selecione o tipo de animal.')]
    )

    pet_breed = StringField(
        'Raça (opcional)',
        validators=[Optional(), Length(max=100)],
        render_kw={'placeholder': 'Ex: Labrador, Siamês, SRD (vira-lata)'}
    )

    pet_color = StringField(
        'Cor / pelagem',
        validators=[Optional(), Length(max=100)],
        render_kw={'placeholder': 'Ex: Caramelo com manchas brancas'}
    )

    pet_size = SelectField(
        'Porte',
        choices=[
            ('', 'Não sei / Não se aplica'),
            ('small', 'Pequeno (até 10kg)'),
            ('medium', 'Médio (10 a 25kg)'),
            ('large', 'Grande (acima de 25kg)')
        ],
        validators=[Optional()]
    )

    cep = StringField(
        'CEP (opcional)',
        validators=[Optional(), Length(max=9)],
        render_kw={
            'placeholder': '00000-000',
            'autocomplete': 'postal-code',
            'inputmode': 'numeric',
        }
    )

    last_seen_location = StringField(
        'Localização (onde foi visto)',
        validators=[
            DataRequired(message='A localização é obrigatória.'),
            Length(max=255)
        ],
        render_kw={'placeholder': 'Ex: Rua das Flores, 123 — Bairro Jardim, São Paulo/SP'}
    )

    contact_phone = StringField(
        'Telefone para contato',
        validators=[
            DataRequired(message='O telefone de contato é obrigatório.'),
            Length(max=20)
        ],
        render_kw={'placeholder': '(11) 99999-9999'}
    )

    contact_email = StringField(
        'Email para contato (opcional)',
        validators=[Optional(), Email(message='Informe um email válido.')],
        render_kw={'placeholder': 'contato@email.com'}
    )

    reward = StringField(
        'Recompensa (opcional)',
        validators=[Optional(), Length(max=100)],
        render_kw={'placeholder': 'Ex: R$ 200,00 de recompensa'}
    )

    # Campo de upload de múltiplas fotos
    # FileAllowed restringe os tipos aceitos
    photos = MultipleFileField(
        'Fotos do pet (máximo 5)',
        validators=[
            FileAllowed(
                ['png', 'jpg', 'jpeg', 'gif', 'webp'],
                message='Apenas imagens são permitidas (PNG, JPG, GIF, WEBP).'
            )
        ]
    )

    submit = SubmitField('Publicar anúncio')

    def validate_photos(self, field):
        """Validação customizada: máximo de 5 fotos por post."""
        if field.data:
            # Filtra apenas arquivos com nome (ignora campos vazios)
            valid_files = [f for f in field.data if f and f.filename]
            if len(valid_files) > 5:
                raise ValidationError('Você pode enviar no máximo 5 fotos por post.')
