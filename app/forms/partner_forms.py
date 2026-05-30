from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Optional, Length, Email, Regexp, URL


class PartnerForm(FlaskForm):
    name = StringField(
        'Nome do local',
        validators=[DataRequired(message='O nome é obrigatório.'), Length(max=150)],
        render_kw={'placeholder': 'Ex: Petshop Amigo Fiel'}
    )

    partner_type = SelectField(
        'Tipo de parceiro',
        choices=[
            ('foster_home', '🏠 Lar Temporário'),
            ('petshop', '🛒 Petshop Parceiro'),
            ('vet_clinic', '🏥 Clínica Veterinária'),
        ],
        validators=[DataRequired()]
    )

    description = TextAreaField(
        'Descrição (opcional)',
        validators=[Optional()],
        render_kw={'placeholder': 'Informações sobre o local, serviços, horários...', 'rows': 3}
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

    address = StringField(
        'Endereço',
        validators=[DataRequired(message='O endereço é obrigatório.'), Length(max=255)],
        render_kw={'placeholder': 'Ex: Pinheiros, São Paulo, SP'}
    )

    phone = StringField(
        'Telefone (opcional)',
        validators=[
            Optional(),
            Regexp(r'^\(\d{2}\) \d{4,5}-\d{4}$', message='Telefone inválido. Use (XX) XXXX-XXXX ou (XX) XXXXX-XXXX.')
        ],
        render_kw={'placeholder': '(11) 99999-9999', 'type': 'tel', 'maxlength': '15'}
    )

    email = StringField(
        'Email (opcional)',
        validators=[Optional(), Email(check_deliverability=False, message='Informe um email válido.')],
        render_kw={'placeholder': 'contato@local.com', 'type': 'email'}
    )

    website = StringField(
        'Site (opcional)',
        validators=[
            Optional(),
            URL(message='Informe uma URL válida (deve começar com http:// ou https://).'),
            Length(max=255),
        ],
        render_kw={'placeholder': 'https://...'}
    )

    is_active = BooleanField('Visível no mapa público', default=True)

    submit = SubmitField('Salvar parceiro')
