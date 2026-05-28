from flask_wtf import FlaskForm
from flask_wtf.file import MultipleFileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Optional, Length, Email, ValidationError


class AdoptionForm(FlaskForm):
    title = StringField(
        'Título do anúncio',
        validators=[
            DataRequired(message='O título é obrigatório.'),
            Length(max=150, message='O título deve ter no máximo 150 caracteres.')
        ],
        render_kw={'placeholder': 'Ex: Cachorro caramelo para adoção em São Paulo'}
    )

    description = TextAreaField(
        'Descrição',
        validators=[DataRequired(message='A descrição é obrigatória.')],
        render_kw={
            'placeholder': 'Conte sobre o pet: personalidade, rotina, como chegou até você...',
            'rows': 5
        }
    )

    pet_name = StringField(
        'Nome do pet (opcional)',
        validators=[Optional(), Length(max=100)],
        render_kw={'placeholder': 'Ex: Mel, Thor, Bolinha...'}
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
        'Cor / pelagem (opcional)',
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

    is_neutered = BooleanField('Castrado')
    is_vaccinated = BooleanField('Vacinado')

    adopter_requirements = TextAreaField(
        'Requisitos para o adotante (opcional)',
        validators=[Optional()],
        render_kw={
            'placeholder': 'Ex: Não ter outros pets, morar em casa com quintal, ter experiência com animais...',
            'rows': 3
        }
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

    location = StringField(
        'Localização do pet',
        validators=[
            DataRequired(message='A localização é obrigatória.'),
            Length(max=255)
        ],
        render_kw={'placeholder': 'Ex: Pinheiros, São Paulo, SP'}
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
        if field.data:
            valid_files = [f for f in field.data if f and f.filename]
            if len(valid_files) > 5:
                raise ValidationError('Você pode enviar no máximo 5 fotos por anúncio.')
