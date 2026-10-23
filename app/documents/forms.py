from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import SubmitField, StringField
from wtforms.validators import DataRequired


class UploadDocumentForm(FlaskForm):
    file = FileField(
        "Choose Document",
        validators=[
            FileRequired(),
            FileAllowed(
                [
                    "pdf",
                    "txt",
                    "doc",
                    "docx",
                    "png",
                    "jpg",
                    "jpeg"
                ],
                "Only PDF, TXT, DOC, DOCX, PNG, JPG and JPEG files are allowed."
            )
        ]
    )

    submit = SubmitField("Upload")


class ShareDocumentForm(FlaskForm):
    email = StringField(
        "Recipient Email",
        validators=[
            DataRequired(message="Recipient email is required.")
        ]
    )

    submit = SubmitField("Share Document")