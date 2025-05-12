import os
from io import BytesIO
from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, send_file, current_app, session
from flask_login import login_required, current_user
from wtforms.validators import DataRequired
from wtforms import SelectField
from models import Case, Document
from forms import FilingToolkitForm
from utils import generate_document, generate_filename

documents = Blueprint('documents', __name__)

@documents.route('/filing-toolkit', methods=['GET', 'POST'])
@login_required
def filing_toolkit():
    form = FilingToolkitForm()
    user_cases = []  # Initialize empty list by default
    
    # Fetch user's cases for the dropdown
    try:
        user_cases = Case.get_cases_by_user(current_user.id)
        case_choices = [(str(case.id), case.title) for case in user_cases]
        
        # Set case choices for dropdown
        form.case_id.choices = [('', 'Select a Case')] + case_choices
        
        if form.validate_on_submit():
            try:
                print(f"Form submitted with data: {form.data}")  # Debug logging
                
                case_id = int(form.case_id.data)
                case = Case.get_case_by_id(case_id)
                
                if not case:
                    flash('Case not found.', 'danger')
                    return redirect(url_for('documents.filing_toolkit'))
                
                if case.user_id != current_user.id and not current_user.is_legal_assistant():
                    flash('You do not have permission to generate documents for this case.', 'danger')
                    return redirect(url_for('documents.filing_toolkit'))
                
                # Calculate deadline information
                deadline_date = form.deadline_date.data
                days_remaining = None
                if deadline_date:
                    days_remaining = (deadline_date - datetime.utcnow().date()).days
                
                print(f"Generating document for case: {case.id}, form type: {form.form_type.data}")  # Debug logging
                
                # Generate document content based on form type
                content = generate_document(
                    form_type=form.form_type.data,
                    case=case,
                    state=form.state.data,
                    court_type=form.court_type.data,
                    deadline_date=deadline_date
                )
                
                # Create filename for the document
                filename = generate_filename(
                    case_name=case.title,
                    form_type=form.form_type.data,
                    state=form.state.data
                )
                
                print(f"Creating document record with filename: {filename}")  # Debug logging
                
                try:
                    # Create document record
                    document = Document.create_document(
                        case_id=case_id,
                        user_id=current_user.id,
                        doc_type=form.form_type.data,
                        state=form.state.data,
                        court_type=form.court_type.data,
                        content=content,
                        filename=filename
                    )
                    
                    print(f"Document created with ID: {document.id}")  # Debug logging
                    
                    # Store the document ID in session for download
                    session['last_document_id'] = document.id
                    
                    flash(f'Document "{filename}" has been generated!', 'success')
                    
                    # Redirect to download or preview the document
                    return redirect(url_for('documents.download_document', document_id=document.id))
                except Exception as e:
                    print(f"ERROR creating document: {str(e)}")  # Debug logging
                    import traceback
                    traceback.print_exc()
                    flash(f'Error creating document: {str(e)}', 'danger')
                    
            except Exception as e:
                print(f"ERROR in form processing: {str(e)}")  # Debug logging
                import traceback
                traceback.print_exc()
                flash(f'Error processing form: {str(e)}', 'danger')
                
    except Exception as e:
        print(f"ERROR in filing_toolkit view: {str(e)}")  # Debug logging
        import traceback
        traceback.print_exc()
        flash(f'Error loading the filing toolkit: {str(e)}', 'danger')
    
    return render_template('filing_toolkit.html', form=form, user_cases=user_cases)

@documents.route('/download/<int:document_id>')
@login_required
def download_document(document_id):
    try:
        print(f"Attempting to download document ID: {document_id}")  # Debug logging
        document = Document.get_document_by_id(document_id)
        
        if not document:
            print(f"Document ID {document_id} not found")  # Debug logging
            flash('Document not found.', 'danger')
            return redirect(url_for('documents.filing_toolkit'))
        
        print(f"Found document: {document.id}, filename: {document.filename}")  # Debug logging
        
        if document.user_id != current_user.id and not current_user.is_moderator() and not current_user.is_legal_assistant():
            flash('You do not have permission to download this document.', 'danger')
            return redirect(url_for('documents.filing_toolkit'))
        
        # Create PDF in memory
        pdf_bytes = BytesIO()
        # This would be replaced with actual PDF generation logic
        pdf_bytes.write(document.content.encode())
        pdf_bytes.seek(0)
        
        print(f"Serving document file: {document.filename}")  # Debug logging
        
        try:
            # Instead of trying to generate a PDF, let's return a simple HTML page with the content
            # This will help us test if the document generation is working
            content_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>{document.filename}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    h1 {{ color: #333; }}
                    pre {{ background: #f5f5f5; padding: 15px; border-radius: 5px; white-space: pre-wrap; }}
                </style>
            </head>
            <body>
                <h1>Document: {document.filename}</h1>
                <p>Generated for Case #{document.case_id}, {document.state} {document.court_type}</p>
                <h2>Document Content:</h2>
                <pre>{document.content}</pre>
                <hr>
                <p><a href="{url_for('documents.filing_toolkit')}">Return to Filing Toolkit</a></p>
            </body>
            </html>
            """
            return content_html
        except Exception as e:
            print(f"ERROR rendering document: {str(e)}")
            # Fallback to basic file download if HTML rendering fails
            return send_file(
                pdf_bytes,
                as_attachment=True,
                download_name=document.filename,
                mimetype='application/pdf'
            )
    except Exception as e:
        print(f"ERROR in download_document: {str(e)}")  # Debug logging
        import traceback
        traceback.print_exc()
        flash(f'Error downloading document: {str(e)}', 'danger')
        return redirect(url_for('documents.filing_toolkit'))
